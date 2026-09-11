import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_se = tables["ii_se"].copy()
    df_vlh = tables["ii_vlh"].copy()

    shock_cols = ["se01a", "se01b", "se01c", "se01d", "se01e", "se01f"]
    se_flags = df_se[["folio"] + shock_cols].drop_duplicates(subset=["folio"]).copy()

    se_flags["any_shock"] = se_flags[shock_cols].eq(1.0).any(axis=1)
    se_flags["all_no"] = se_flags[shock_cols].eq(3.0).all(axis=1)

    vlh_subset = df_vlh[["folio", "vlh18a"]].drop_duplicates(subset=["folio"])

    merged = pd.merge(se_flags[["folio", "any_shock", "all_no"]], vlh_subset, on="folio", how="inner")

    mean_no = merged.loc[merged["all_no"], "vlh18a"].mean(skipna=True)

    if pd.isna(mean_no):
        return pd.DataFrame({"folio": pd.Series(dtype="object"), "vlh18a": pd.Series(dtype="float64")})

    result = merged.loc[(merged["any_shock"]) & (merged["vlh18a"] > mean_no), ["folio", "vlh18a"]].copy()

    return result.reset_index(drop=True)