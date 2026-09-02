import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_crh = tables["ii_crh"]

    # Households in Oaxaca with at least one member aged 60+ (proxied by interviewed person's age)
    df_portad_cond = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 60.0)]

    # Households that report feeling unsafe or very unsafe at home
    df_vlh_cond = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]]

    # Households that incurred credit/loan debt in the last 12 months with a stated amount
    df_crh_cond = df_crh[(df_crh["crh02_1"] == 1.0) & (df_crh["crh02_2"].notna())][["folio"]]

    # Intersection of conditions
    result = (
        df_portad_cond[["folio"]]
        .merge(df_vlh_cond, on="folio", how="inner")
        .merge(df_crh_cond, on="folio", how="inner")
        .drop_duplicates()
    )

    return pd.DataFrame({"households_count": [len(result)]})