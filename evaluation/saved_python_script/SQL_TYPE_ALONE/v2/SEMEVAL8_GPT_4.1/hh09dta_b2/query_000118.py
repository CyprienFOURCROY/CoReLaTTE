def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one adult (edad >= 18)
    df_adults = df_oaxaca[df_oaxaca["edad"] >= 18.0]
    adult_households = df_adults["folio"].unique()

    # 3. Households that did NOT receive Liconsa milk in last 12 months (in03a == 3)
    df_in_oaxaca = df_in[df_in["folio"].isin(adult_households)]
    df_no_liconsa = df_in_oaxaca[df_in_oaxaca["in03a"] == 3.0]
    no_liconsa_households = df_no_liconsa["folio"].unique()

    # 4. Households with positive total debts+interests (crh04_2 > 0)
    df_crh_oaxaca = df_crh[df_crh["folio"].isin(no_liconsa_households)]
    df_crh_positive_debt = df_crh_oaxaca[df_crh_oaxaca["crh04_2"] > 0]
    positive_debt_households = df_crh_positive_debt["folio"].unique()

    # 5. Households that directly received a positive amount from Other Government Program (in02a10 > 0)
    df_in_positive_othergov = df_in[
        (df_in["folio"].isin(positive_debt_households)) &
        (df_in["in02a10"].notna()) &
        (df_in["in02a10"] > 0)
    ]
    final_households = df_in_positive_othergov["folio"].unique()

    # 6. Compute average total debts+interests for these households
    df_crh_final = df_crh[
        (df_crh["folio"].isin(final_households)) &
        (df_crh["crh04_2"].notna()) &
        (df_crh["crh04_2"] > 0)
    ]
    avg_debt = df_crh_final["crh04_2"].mean()

    # 7. Households with total debts+interests > average
    df_crh_above_avg = df_crh_final[df_crh_final["crh04_2"] > avg_debt]
    above_avg_households = df_crh_above_avg["folio"].unique()

    # 8. Count unique households
    count = len(above_avg_households)

    return pd.DataFrame({"households_count": [count]})