def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]

    # 1. Households where a member died in last 5 years: se01a == 1
    died_hh = df_se[df_se["se01a"] == 1][["folio"]].drop_duplicates()

    # 2. Households with at least one member aged 65+
    aged_65plus = df_portad[df_portad["edad"] >= 65][["folio"]].drop_duplicates()

    # 3. Households with at least one member aged <18
    aged_under18 = df_portad[df_portad["edad"] < 18][["folio"]].drop_duplicates()

    # 4. Merge to get households that satisfy all three conditions
    merged = died_hh.merge(aged_65plus, on="folio").merge(aged_under18, on="folio")

    # 5. Count unique households
    count = merged["folio"].nunique()

    return pd.DataFrame({"households": [count]})