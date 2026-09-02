def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one member aged 25–54
    oaxaca_25_54 = oaxaca_portad[(oaxaca_portad["edad"] >= 25) & (oaxaca_portad["edad"] <= 54)]
    hh_with_25_54 = set(oaxaca_25_54["folio"].unique())

    # 3. Households with at least one member owning financial assets/afores (ah03h == 1)
    oaxaca_ah = df_ah[df_ah["folio"].isin(oaxaca_portad["folio"])]
    owns_fin_assets = oaxaca_ah[oaxaca_ah["ah03h"] == 1.0]
    hh_with_fin_assets = set(owns_fin_assets["folio"].unique())

    # 4. Households with at least one member aged 25–54 AND at least one member owning financial assets/afores
    hh_target = hh_with_25_54 & hh_with_fin_assets

    # 5. For these households, get their crh04_2 (total debts + interests, value in pesos)
    oaxaca_crh = df_crh[df_crh["folio"].isin(oaxaca_portad["folio"])]
    # Only keep rows with valid crh04_2 (not null)
    oaxaca_crh_debt = oaxaca_crh[oaxaca_crh["crh04_2"].notnull()]
    # Only households with at least one member aged 25–54
    hh_with_25_54_and_debt = set(oaxaca_crh_debt[oaxaca_crh_debt["folio"].isin(hh_with_25_54)]["folio"].unique())
    # Compute average crh04_2 among these households (with 25–54yo and recorded debt)
    # For each household, get the max crh04_2 (in case of multiple members per household)
    crh_debt_max = oaxaca_crh_debt[oaxaca_crh_debt["folio"].isin(hh_with_25_54)].groupby("folio")["crh04_2"].max()
    avg_debt = crh_debt_max.mean()

    # 6. For the target households, get their max crh04_2 (if any)
    crh_debt_target = oaxaca_crh_debt[oaxaca_crh_debt["folio"].isin(hh_target)]
    crh_debt_target_max = crh_debt_target.groupby("folio")["crh04_2"].max()

    # 7. Count households with crh04_2 > avg_debt
    count = (crh_debt_target_max > avg_debt).sum()

    return pd.DataFrame({"households_above_avg_debt": [int(count)]})