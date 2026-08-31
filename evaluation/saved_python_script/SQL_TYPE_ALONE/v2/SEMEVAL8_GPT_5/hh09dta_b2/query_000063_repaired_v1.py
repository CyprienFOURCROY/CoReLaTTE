import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()

    # Filter adults (18+) in Oaxaca (ent == 20)
    adults_oaxaca = df_portad[
        (df_portad["ent"] == 20) &
        (df_portad["edad"].notna()) &
        (df_portad["edad"] >= 18)
    ][["folio", "edad"]]

    # Households that own/share a non-ag business
    hh_nonag = df_nna[df_nna["nna01"] == 1].drop_duplicates(subset=["folio"])

    # Households that received a positive amount directly from Other Government Program
    hh_other_gov_pos = df_in[(df_in["in02a10"].notna()) & (df_in["in02a10"] > 0)].drop_duplicates(subset=["folio"])

    # Merge filters
    subset = (
        adults_oaxaca
        .merge(hh_nonag, on="folio", how="inner")
        .merge(hh_other_gov_pos, on="folio", how="inner")
    )

    if subset.empty:
        count = 0
    else:
        mean_age = subset["edad"].mean()
        if np.isnan(mean_age):
            count = 0
        else:
            count = int((subset["edad"] > mean_age).sum())

    return pd.DataFrame({"count": [count]})