import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    hh_any70 = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), has70=("edad", lambda s: (s >= 70).any()))
    )
    hh_any70 = hh_any70[hh_any70["has70"]]

    df_in = tables["ii_in"][["folio", "in01a11_1"]].copy()
    hh_70ymas = df_in[df_in["in01a11_1"] == 1.0][["folio"]].drop_duplicates()

    df_vlh = tables["ii_vlh"][["folio", "vlh04", "vlh10c"]].copy()
    mask_unsafe = df_vlh["vlh04"].isin([3.0, 4.0])
    mask_no_kidn = df_vlh["vlh10c"] == 3.0
    hh_vlh = df_vlh[mask_unsafe & mask_no_kidn][["folio"]].drop_duplicates()

    eligible = (
        hh_any70.merge(hh_70ymas, on="folio", how="inner")
        .merge(hh_vlh, on="folio", how="inner")
    )

    result = (
        eligible.groupby("ent", as_index=False)
        .agg(households=("folio", "nunique"))
    )

    result = result[result["households"] >= 10]
    result = result.sort_values("households", ascending=False).reset_index(drop=True)
    return result