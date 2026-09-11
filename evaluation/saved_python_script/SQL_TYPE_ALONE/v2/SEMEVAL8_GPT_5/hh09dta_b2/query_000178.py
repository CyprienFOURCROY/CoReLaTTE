import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_nna = tables["ii_nna"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Households in Oaxaca with at least one adult (18+)
    df_portad["adult"] = df_portad["edad"] >= 18
    hh = df_portad.groupby("folio").agg(ent=("ent", "first"), has_adult=("adult", "any")).reset_index()
    hh_oax = hh[(hh["ent"] == 20.0) & (hh["has_adult"])][["folio"]]

    # Statewide (Oaxaca) average of vlh18a among households with at least one adult
    vlh_unique = df_vlh[["folio", "vlh18a"]].drop_duplicates(subset=["folio"])
    oax_vlh = hh_oax.merge(vlh_unique, on="folio", how="left")
    statewide_avg = oax_vlh["vlh18a"].mean()

    # Filter households that own/share a non-ag business and have vlh18a >= statewide average
    nna_unique = df_nna[["folio", "nna01"]].drop_duplicates(subset=["folio"])
    eligible = (
        hh_oax.merge(nna_unique, on="folio", how="inner")
        .merge(vlh_unique, on="folio", how="left")
    )
    eligible = eligible[(eligible["nna01"] == 1.0) & (eligible["vlh18a"] >= statewide_avg)]

    result_avg = eligible["vlh18a"].mean()

    return pd.DataFrame({"average_vlh18a": [result_avg]})