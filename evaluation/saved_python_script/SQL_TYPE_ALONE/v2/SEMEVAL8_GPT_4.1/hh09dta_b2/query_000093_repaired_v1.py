def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one member aged 70 or older
    df_70plus = df_oaxaca[df_oaxaca["edad"] >= 70.0]
    folios_70plus = df_70plus["folio"].unique()

    # 3. Households that received income from an Other Government Program in the last 12 months
    # in01a10_1 == 1 means: Participates in the program and have received income
    df_in_ogp = df_in[df_in["in01a10_1"] == 1.0]
    folios_ogp = df_in_ogp["folio"].unique()

    # 4. Households that reported an amount paid on credit/loans in the last year
    # crh03_1 == 1 means: Value (i.e., they paid something)
    df_crh_paid = df_crh[df_crh["crh03_1"] == 1.0]
    folios_paid = df_crh_paid["folio"].unique()

    # 5. Households with total debts + interests reported (crh04_1 == 1) and value present
    df_crh_debt = df_crh[(df_crh["crh04_1"] == 1.0) & (~df_crh["crh04_2"].isna())]
    folios_debt = df_crh_debt["folio"].unique()

    # 6. Intersection of all conditions
    folios_final = set(folios_70plus) & set(folios_ogp) & set(folios_paid) & set(folios_debt)

    # 7. Get debt values for these households
    df_debts = df_crh_debt[df_crh_debt["folio"].isin(folios_final)][["folio", "crh04_2"]]

    # 8. Compute group average
    avg_debt = df_debts["crh04_2"].mean()

    # 9. Filter for debts above the group average
    df_above_avg = df_debts[df_debts["crh04_2"] > avg_debt].copy()

    # 10. Sort from highest to lowest
    df_above_avg = df_above_avg.sort_values("crh04_2", ascending=False)

    # 11. Rename columns for clarity
    df_above_avg = df_above_avg.rename(columns={"folio": "household_id", "crh04_2": "total_debt_pesos"})

    df_above_avg.reset_index(drop=True, inplace=True)
    return df_above_avg