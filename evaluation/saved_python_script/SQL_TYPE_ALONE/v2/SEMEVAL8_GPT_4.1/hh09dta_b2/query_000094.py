def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_vlh = tables["ii_vlh"]

    # 1. Filter Oaxaca individuals
    df_oax = df_portad[df_portad["ent"] == 20.0]

    # 2. Compute average age in Oaxaca
    avg_age = df_oax["edad"].mean()

    # 3. Individuals older than average age in Oaxaca
    df_oax_older = df_oax[df_oax["edad"] > avg_age]

    # 4. Households that reported knowing a family/friend robbed in last 12 months (vlh10a == 1)
    df_vlh_robbed12m = df_vlh[df_vlh["vlh10a"] == 1.0][["folio"]].drop_duplicates()

    # 5. Households that reported NO household member death in last 5 years (se01a == 3)
    df_se_no_death = df_se[df_se["se01a"] == 3.0][["folio"]].drop_duplicates()

    # 6. Merge to get individuals in Oaxaca, older than average, in households that meet both conditions
    df_merge = df_oax_older.merge(df_vlh_robbed12m, on="folio", how="inner")
    df_merge = df_merge.merge(df_se_no_death, on="folio", how="inner")

    # 7. Count individuals
    count = len(df_merge)

    return pd.DataFrame({"count": [count]})