def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_in = tables["ii_in"]

    # Step 1: Find households where at least one member owns a motor vehicle (ah03d == 1)
    motor_vehicle_owners = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # Step 2: For these households, get their state from df_portad (one row per household)
    # Since folio is household id, get one row per household from df_portad
    households_with_state = df_portad.drop_duplicates(subset=["folio"])[["folio", "ent"]]

    # Merge to get state for households with a motor vehicle owner
    mv_households = motor_vehicle_owners.merge(households_with_state, on="folio", how="inner")

    # Step 3: For these households, get the amount received directly from Other Government Program (in02a10)
    # Merge with df_in to get in02a10
    mv_households_in = mv_households.merge(df_in[["folio", "in02a10"]], on="folio", how="left")

    # Step 4: For each household, keep only those with in02a10 > 0 (positive amount received)
    mv_households_in_pos = mv_households_in[(mv_households_in["in02a10"].notna()) & (mv_households_in["in02a10"] > 0)]

    # Step 5: For each state, count number of unique households with at least one member owning a motor vehicle
    mv_households_count = mv_households[["folio", "ent"]].drop_duplicates().groupby("ent").size().reset_index(name="n_households")

    # Step 6: Filter to states with at least 50 such households
    eligible_states = mv_households_count[mv_households_count["n_households"] >= 50]["ent"]

    # Step 7: For these states, compute the average in02a10 among households with positive amount
    result = (
        mv_households_in_pos[mv_households_in_pos["ent"].isin(eligible_states)]
        .groupby("ent")["in02a10"]
        .mean()
        .reset_index()
        .rename(columns={"ent": "state", "in02a10": "avg_in02a10"})
        .sort_values("avg_in02a10", ascending=False)
        .reset_index(drop=True)
    )

    return result