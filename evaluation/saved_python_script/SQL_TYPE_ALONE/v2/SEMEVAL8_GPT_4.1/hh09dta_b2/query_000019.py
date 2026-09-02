def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]

    # 1. Oaxaca households: ent == 20
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0]["folio"]

    # 2. Households with positive total debt (including interest): crh04_2 > 0
    df_crh_debt = df_crh[df_crh["crh04_2"].notna() & (df_crh["crh04_2"] > 0)]

    # 3. Households that feel unsafe or very unsafe at home: vlh04 in [3, 4]
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]

    # 4. Households that disagree or completely disagree that their locality is close-knit: vlh01k in [3, 4]
    df_vlh_not_close = df_vlh[df_vlh["vlh01k"].isin([3.0, 4.0])]

    # 5. Merge all conditions
    # Start with Oaxaca folios
    folios_oaxaca = set(oaxaca_folios)

    # Only keep folios present in all three tables
    folios_debt = set(df_crh_debt["folio"])
    folios_unsafe = set(df_vlh_unsafe["folio"])
    folios_not_close = set(df_vlh_not_close["folio"])

    # Intersection of all conditions
    folios_final = folios_oaxaca & folios_debt & folios_unsafe & folios_not_close

    # Get the debt values for these folios
    df_final = df_crh_debt[df_crh_debt["folio"].isin(folios_final)]

    # Compute average and count
    if not df_final.empty:
        avg_debt = df_final["crh04_2"].mean()
        count = df_final["folio"].nunique()
    else:
        avg_debt = np.nan
        count = 0

    return pd.DataFrame({
        "average_debt_pesos": [avg_debt],
        "num_households": [count]
    })