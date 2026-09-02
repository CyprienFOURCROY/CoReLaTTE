def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_su = tables["ii_su"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20.0]["folio"].unique()

    # 2. Households that use a plot/land for sowing/farming/vegetable (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1.0]["folio"].unique()

    # 3. Households that reported a household member died in last 5 years (se01a == 1)
    se_died = df_se[df_se["se01a"] == 1.0]["folio"].unique()

    # 4. Intersection: Oaxaca & plot & death
    result_folios = set(oaxaca_households) & set(su_plot) & set(se_died)

    count = len(result_folios)

    return pd.DataFrame({"households": [count]})