def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_se = tables["ii_se"]

    # 1. Households in Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one member aged 60 or older
    df_60plus = df_oaxaca[df_oaxaca["edad"] >= 60.0][["folio"]].drop_duplicates()

    # 3. Households where at least one member feels unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]].drop_duplicates()

    # 4. Households that reported a household member’s death in the last five years (se01a == 1)
    df_se_death = df_se[df_se["se01a"] == 1.0][["folio"]].drop_duplicates()

    # 5. Intersection: households that meet all three criteria
    folios = set(df_60plus["folio"]) & set(df_vlh_unsafe["folio"]) & set(df_se_death["folio"])

    result = pd.DataFrame({"households_count": [len(folios)]})
    return result