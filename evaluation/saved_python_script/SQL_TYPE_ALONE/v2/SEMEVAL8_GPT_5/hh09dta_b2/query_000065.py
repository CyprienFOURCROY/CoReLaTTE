import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_nna = tables["ii_nna"].copy()

    # Households where at least one member owns both an electronic device and a washing machine/stove
    has_both_assets = ((df_ah["ah03e"] == 1.0) & (df_ah["ah03f"] == 1.0))
    hh_assets = (
        df_ah.assign(has_both=has_both_assets)
        .groupby("folio", as_index=False)["has_both"]
        .any()
    )

    # Households where at least one member owns or shares a non-ag business
    has_nonag = (df_nna["nna01"] == 1.0)
    hh_nonag = (
        df_nna.assign(has_nonag=has_nonag)
        .groupby("folio", as_index=False)["has_nonag"]
        .any()
    )

    # Households satisfying both conditions
    hh_ok = hh_assets.merge(hh_nonag, on="folio", how="inner")
    hh_ok = hh_ok[(hh_ok["has_both"]) & (hh_ok["has_nonag"])]

    # Adults (18+) in those households
    adults = df_portad[df_portad["edad"] >= 18]
    adults_ok = adults.merge(hh_ok[["folio"]], on="folio", how="inner")

    # Group by state and compute average age and count of adults
    result = (
        adults_ok.groupby("ent")
        .agg(average_age=("edad", "mean"), adult_count=("edad", "size"))
        .reset_index()
        .sort_values(["average_age", "adult_count"], ascending=[False, False])
        .head(10)
    )

    return result