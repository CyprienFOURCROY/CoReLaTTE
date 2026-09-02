def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0]["folio"]

    # 2. Households that reported a disease/accident/hospitalization event in last 5 years (se01b == 1)
    se_disease = df_se[df_se["se01b"] == 1.0]

    # 3. Intersection: Oaxaca + disease event
    folios = set(oaxaca_folios).intersection(se_disease["folio"])

    # 4. Get crh04_2 (total debts + interests, pesos) for these households
    crh_filtered = df_crh[df_crh["folio"].isin(folios)]

    # Only consider those with a recorded value (not null) for crh04_2
    crh_with_value = crh_filtered[crh_filtered["crh04_2"].notnull()]

    # 5. Compute average among these households
    avg_debt = crh_with_value["crh04_2"].mean()

    # 6. Count how many have value above the average
    count_above_avg = (crh_with_value["crh04_2"] > avg_debt).sum()

    return pd.DataFrame({"households_above_avg_debt": [int(count_above_avg)]})