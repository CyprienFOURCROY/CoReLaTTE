def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]
    df_crh = tables["ii_crh"]

    # 1. Adults (age 18+) in Oaxaca (ent==20)
    adults_oaxaca = df_portad[(df_portad["edad"] >= 18) & (df_portad["ent"] == 20.0)].copy()

    # 2. Households with disease/accident/hospitalization event in last 5 years (se01b==1)
    se_disease = df_se[df_se["se01b"] == 1.0][["folio"]].drop_duplicates()

    # 3. Households with at least one member who owns an electronic device (ah03e==1)
    ah_electronic = df_ah[df_ah["ah03e"] == 1.0][["folio"]].drop_duplicates()

    # 4. Households with at least one member who owns/shares a non-ag business (nna01==1)
    nna_business = df_nna[df_nna["nna01"] == 1.0][["folio"]].drop_duplicates()

    # 5. Households whose total household debt (crh04_1==1) exceeds the average among indebted households in Oaxaca
    # First, get indebted households in Oaxaca (ent==20)
    # Join crh with portad to get ent
    crh_with_ent = df_crh.merge(df_portad[["folio", "ent"]].drop_duplicates(), on="folio", how="left")
    indebted_oaxaca = crh_with_ent[(crh_with_ent["ent"] == 20.0) & (crh_with_ent["crh04_1"] == 1.0) & (~crh_with_ent["crh04_2"].isna())]
    # Compute average debt among indebted households in Oaxaca
    avg_debt = indebted_oaxaca["crh04_2"].mean()
    # Households with debt > avg_debt
    high_debt_folios = indebted_oaxaca[indebted_oaxaca["crh04_2"] > avg_debt][["folio"]].drop_duplicates()

    # 6. Intersect all conditions on folio
    # Get folios that satisfy all conditions
    folios = set(se_disease["folio"]) & set(ah_electronic["folio"]) & set(nna_business["folio"]) & set(high_debt_folios["folio"])

    # 7. Adults in Oaxaca living in those households
    result = adults_oaxaca[adults_oaxaca["folio"].isin(folios)]

    # 8. Return count
    return pd.DataFrame({"num_adults": [result.shape[0]]})