import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_ah = tables["ii_ah"][["folio", "ah03h"]]
    df_vlh = tables["ii_vlh"][["folio", "vlh18a"]]
    df_nna = tables["ii_nna"][["folio", "nna01"]]

    # Households with at least one member owning financial assets/afores
    hh_assets = df_ah.loc[df_ah["ah03h"] == 1, "folio"].dropna().drop_duplicates()

    # Average vlh18a among households that do not own/share a non-ag business
    df_nna_vlh = df_nna.merge(df_vlh, on="folio", how="left")
    avg_nonbiz = df_nna_vlh.loc[df_nna_vlh["nna01"] == 2, "vlh18a"].mean()

    # Select households with assets and vlh18a > average of non-business owners
    res = df_vlh[df_vlh["folio"].isin(hh_assets)].copy()
    res = res[res["vlh18a"] > avg_nonbiz]

    return res[["folio", "vlh18a"]].reset_index(drop=True)