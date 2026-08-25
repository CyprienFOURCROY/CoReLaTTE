import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_se = tables["ii_se"][["folio", "se01a"]].copy()
    df_portad = tables["ii_portad"][["folio", "ent"]].drop_duplicates(subset=["folio"])
    df_nna = tables["ii_nna"][["folio", "nna01", "nna02"]].copy()

    death_hh = df_se[df_se["se01a"] == 1.0][["folio"]].drop_duplicates()
    if death_hh.empty:
        return pd.DataFrame({"ent": pd.Series(dtype="float64"),
                             "avg_non_ag_businesses": pd.Series(dtype="float64"),
                             "households": pd.Series(dtype="int64")})

    merged = (
        death_hh
        .merge(df_portad, on="folio", how="left")
        .merge(df_nna, on="folio", how="left")
    )

    merged["num_business"] = np.where(merged["nna01"] == 1.0, merged["nna02"].fillna(0), 0)

    result = (
        merged.groupby("ent", dropna=True)
        .agg(
            avg_non_ag_businesses=("num_business", "mean"),
            households=("folio", "nunique"),
        )
        .reset_index()
        .sort_values(by="avg_non_ag_businesses", ascending=False, kind="mergesort")
        .reset_index(drop=True)
    )

    return result