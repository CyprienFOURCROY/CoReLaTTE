def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # Filter Oaxaca households
    df_oax = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # Merge with crh for credit/loans and total debts+interest
    df_crh_sel = df_crh[
        df_crh["folio"].notna() &
        df_crh["crh02_2"].notna() &
        df_crh["crh04_2"].notna()
    ][["folio", "crh02_2", "crh04_2"]]

    # Only Oaxaca
    df_oax_crh = df_oax.merge(df_crh_sel, on="folio", how="inner")

    # For asset ownership, get one row per household (any member with a motor vehicle)
    df_ah_mv = df_ah[df_ah["ah03d"].notna()][["folio", "ah03d"]]
    # 1: Yes, 3: No
    df_ah_mv["owns_motor_vehicle"] = np.where(df_ah_mv["ah03d"] == 1.0, 1, 0)
    # Aggregate to household: if any member owns, household owns
    df_mv = df_ah_mv.groupby("folio", as_index=False)["owns_motor_vehicle"].max()

    # Merge with Oaxaca+crh
    df_final = df_oax_crh.merge(df_mv, on="folio", how="left")
    # Households with no info on ah03d are assumed to not own a motor vehicle
    df_final["owns_motor_vehicle"] = df_final["owns_motor_vehicle"].fillna(0).astype(int)

    # Group by ownership and calculate mean and count
    result = df_final.groupby("owns_motor_vehicle").agg(
        avg_total_debts_plus_interest=("crh04_2", "mean"),
        household_count=("folio", "nunique")
    ).reset_index()

    # Map 1/0 to Yes/No for clarity
    result["owns_motor_vehicle"] = result["owns_motor_vehicle"].map({1: "Yes", 0: "No"})

    return result[["owns_motor_vehicle", "avg_total_debts_plus_interest", "household_count"]]