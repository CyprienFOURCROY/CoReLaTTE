import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()

    su_yes = df_su[df_su["su01"] == 1.0][["folio"]].drop_duplicates()
    nna_yes = df_nna[df_nna["nna01"] == 1.0][["folio"]].drop_duplicates()

    hh_both = su_yes.merge(nna_yes, on="folio", how="inner")

    folio_ent = df_portad.dropna(subset=["ent"])[["folio", "ent"]].drop_duplicates(subset=["folio"], keep="first")
    hh_with_ent = hh_both.merge(folio_ent, on="folio", how="left").dropna(subset=["ent"])

    result = (
        hh_with_ent.groupby("ent", as_index=False)["folio"]
        .nunique()
        .rename(columns={"folio": "households"})
    )

    result["ent"] = result["ent"].astype("int64")
    result = result.sort_values(["households", "ent"], ascending=[False, True]).reset_index(drop=True)
    return result