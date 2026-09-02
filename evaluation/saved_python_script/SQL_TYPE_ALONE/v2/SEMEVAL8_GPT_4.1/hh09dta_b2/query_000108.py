def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one member aged 60 or older
    df_60plus = df_oaxaca[df_oaxaca["edad"] >= 60.0]
    folios_60plus = set(df_60plus["folio"].unique())

    # 3. Households where at least one member reports feeling unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]
    folios_unsafe = set(df_vlh_unsafe["folio"].unique())

    # 4. Households that reported having incurred credit/loan debt in the last 12 months with a stated amount
    # crh02_1 == 1 (Value) and crh02_2 not null
    df_crh_debt = df_crh[(df_crh["crh02_1"] == 1.0) & (~df_crh["crh02_2"].isnull())]
    folios_debt = set(df_crh_debt["folio"].unique())

    # 5. Intersection of all three sets
    folios_final = folios_60plus & folios_unsafe & folios_debt

    # 6. Count unique households
    count = len(folios_final)

    return pd.DataFrame({"households": [count]})