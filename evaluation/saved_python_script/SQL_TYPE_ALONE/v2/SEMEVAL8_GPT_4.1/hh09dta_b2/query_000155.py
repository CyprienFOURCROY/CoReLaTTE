def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # 1. Filter Oaxaca households
    oaxaca_households = df_portad[df_portad["ent"] == 20.0]["folio"].unique()

    # 2. For these households, check if at least one member owns a motor vehicle (ah03d == 1)
    ah_mv = df_ah[(df_ah["folio"].isin(oaxaca_households)) & (df_ah["ah03d"] == 1.0)]
    folios_with_mv = set(ah_mv["folio"].unique())

    # 3. For these households, check if at least one member owns financial assets/afores (ah03h == 1)
    ah_fa = df_ah[(df_ah["folio"].isin(oaxaca_households)) & (df_ah["ah03h"] == 1.0)]
    folios_with_fa = set(ah_fa["folio"].unique())

    # 4. Households with at least one member with both
    folios_both = folios_with_mv & folios_with_fa

    if not folios_both:
        return pd.DataFrame({"average_total_debts_plus_interest": [np.nan]})

    # 5. Get crh04_2 for these households (total debts + interests, in pesos)
    crh_filtered = df_crh[df_crh["folio"].isin(folios_both)]

    # Only consider rows where crh04_2 is not null
    crh_filtered = crh_filtered[crh_filtered["crh04_2"].notnull()]

    if crh_filtered.empty:
        return pd.DataFrame({"average_total_debts_plus_interest": [np.nan]})

    avg_debt = crh_filtered["crh04_2"].mean()

    return pd.DataFrame({"average_total_debts_plus_interest": [avg_debt]})