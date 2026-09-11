import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    # Filter to Oaxaca
    df_oax = df_portad[df_portad["ent"] == 20]

    # Compute household-level age conditions
    hh_age_flags = (
        df_oax.assign(ge60=df_oax["edad"] >= 60, lt30=df_oax["edad"] < 30)
        .groupby("folio")
        .agg(has_ge60=("ge60", "any"), has_lt30=("lt30", "any"))
        .reset_index()
    )
    target_hhs = hh_age_flags[hh_age_flags["has_ge60"] & hh_age_flags["has_lt30"]][["folio"]]

    # Get business ownership at household level
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()
    nna_by_hh = df_nna.groupby("folio", as_index=False).agg(nna01=("nna01", "first"))

    merged = target_hhs.merge(nna_by_hh, on="folio", how="left")
    merged = merged[merged["nna01"].isin([1.0, 2.0])].copy()
    merged["nna01"] = merged["nna01"].map({1.0: "Yes", 2.0: "No"})

    result = (
        merged.groupby("nna01")
        .size()
        .reset_index(name="households")
        .sort_values("nna01")
        .reset_index(drop=True)
    )
    return result