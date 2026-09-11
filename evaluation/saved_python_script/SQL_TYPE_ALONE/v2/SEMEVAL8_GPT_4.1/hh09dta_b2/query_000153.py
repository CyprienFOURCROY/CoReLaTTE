def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_in = tables["ii_in"]

    # 1. Find households with at least one member aged 60 or older
    seniors = df_portad[df_portad["edad"] >= 60]
    senior_households = seniors["folio"].unique()

    # 2. For these households, get their total debts + interests (crh04_2)
    crh_senior = df_crh[df_crh["folio"].isin(senior_households)]
    # Only keep rows with positive debts
    crh_senior_pos = crh_senior[(crh_senior["crh04_2"].notna()) & (crh_senior["crh04_2"] > 0)]
    # Group by household, take the max (in case of multiple rows per household)
    crh_senior_pos_max = crh_senior_pos.groupby("folio", as_index=False)["crh04_2"].max()

    # 3. Compute the average debt among these senior households with positive debts
    avg_debt = crh_senior_pos_max["crh04_2"].mean()

    # 4. Select households whose debt is above the average
    above_avg_debt = crh_senior_pos_max[crh_senior_pos_max["crh04_2"] > avg_debt]
    above_avg_folios = above_avg_debt["folio"].unique()

    # 5. For these households, get the amount received directly from Other Government Program (in02a10)
    df_in_sel = df_in[df_in["folio"].isin(above_avg_folios)]
    # Only consider households that reported receiving it (in02a10 > 0 and not null)
    df_in_sel = df_in_sel[df_in_sel["in02a10"].notna() & (df_in_sel["in02a10"] > 0)]

    # 6. Compute the average amount
    if len(df_in_sel) == 0:
        avg_amount = np.nan
    else:
        avg_amount = df_in_sel["in02a10"].mean()

    return pd.DataFrame({"average_in02a10": [avg_amount]})