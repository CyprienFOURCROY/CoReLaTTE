import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_nna = tables["ii_nna"].copy()

    # Households in Oaxaca (ent == 20)
    oax_folios = pd.Index(df_portad.loc[df_portad["ent"] == 20.0, "folio"].dropna().unique())

    # Households with at least one member who owns an electronic device (ah03e == 1)
    df_ah_sub = df_ah[["folio", "ah03e"]].dropna(subset=["folio"])
    has_elec = (
        df_ah_sub.assign(has_elec=(df_ah_sub["ah03e"] == 1.0))
        .groupby("folio", as_index=False)["has_elec"]
        .any()
    )
    has_elec_folios = pd.Index(has_elec.loc[has_elec["has_elec"], "folio"])

    # Target households: in Oaxaca and with at least one electronic device
    target_folios = oax_folios.intersection(has_elec_folios)

    # Business ownership status from ii_nna (nna01: 1 Yes, 2 No)
    df_nna_sub = df_nna.loc[df_nna["folio"].isin(target_folios), ["folio", "nna01"]].dropna(subset=["folio"])
    df_nna_agg = (
        df_nna_sub.sort_values(by=["folio"])
        .groupby("folio", as_index=False, sort=False)
        .agg({"nna01": "first"})
    )
    df_nna_agg = df_nna_agg[df_nna_agg["nna01"].isin([1.0, 2.0])]

    counts = df_nna_agg["nna01"].value_counts().reindex([1.0, 2.0], fill_value=0)
    result = pd.DataFrame({
        "owns_non_ag_business": ["Yes", "No"],
        "households": [int(counts.loc[1.0]), int(counts.loc[2.0])]
    })
    return result