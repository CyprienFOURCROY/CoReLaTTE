import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]]
    df_se = tables["ii_se"][["folio", "se01a"]]

    # Households in Oaxaca with at least one member aged 60+
    hh_oax_60plus = (
        df_portad.loc[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 60.0), ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates()
    )

    # Households that feel unsafe or very unsafe at home
    hh_unsafe = (
        df_vlh.loc[df_vlh["vlh04"].isin([3.0, 4.0]), ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates()
    )

    # Households that reported a member’s death in the last five years
    hh_death = (
        df_se.loc[df_se["se01a"] == 1.0, ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates()
    )

    eligible = hh_oax_60plus.merge(hh_unsafe, on="folio", how="inner").merge(hh_death, on="folio", how="inner")
    count = eligible["folio"].nunique()

    return pd.DataFrame({"households_count": [count]})