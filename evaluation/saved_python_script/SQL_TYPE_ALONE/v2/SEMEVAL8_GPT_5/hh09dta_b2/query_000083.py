import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]

    # Households with at least one adult member (edad >= 18)
    adult_folios = set(df_portad.loc[df_portad["edad"] >= 18, "folio"].dropna().unique())

    # Households with at least one member owning the dwelling they live in (ah03a == 1)
    owner_folios = set(df_ah.loc[df_ah["ah03a"] == 1.0, "folio"].dropna().unique())

    # Households reporting unsafe or very unsafe at home and agreeing that locality is close
    vlh_mask = df_vlh["vlh04"].isin([3.0, 4.0]) & df_vlh["vlh01k"].isin([1.0, 2.0])
    unsafe_close_folios = set(df_vlh.loc[vlh_mask, "folio"].dropna().unique())

    # Intersection of all conditions
    qualifying_folios = adult_folios & owner_folios & unsafe_close_folios
    count = len(qualifying_folios)

    return pd.DataFrame({"households_count": [count]})