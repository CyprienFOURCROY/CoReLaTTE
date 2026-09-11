import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["edad", "ent", "folio"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh12a_a"]].copy()
    df_ah = tables["ii_ah"][["folio", "ah03m"]].copy()

    # Adults (18+) in Oaxaca (ent == 20)
    adults_oax = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)].copy()

    # Households with forced-entry robbery of current dwelling since 2005 (vlh12a_a == 1)
    robbed_folios = set(df_vlh.loc[df_vlh["vlh12a_a"] == 1.0, "folio"].dropna().unique())

    # Filter adults living in those households
    adults = adults_oax[adults_oax["folio"].isin(robbed_folios)].copy()
    adults = adults.dropna(subset=["edad"])

    # Household-level poultry ownership: any member owns poultry (ah03m == 1)
    ah_poultry = (
        df_ah.assign(owns_poultry=lambda d: (d["ah03m"] == 1.0).astype(bool))
        .groupby("folio", as_index=False)["owns_poultry"]
        .any()
    )
    ah_poultry["owns_poultry"] = ah_poultry["owns_poultry"].astype(int)

    # Merge poultry indicator to adults
    adults = adults.merge(ah_poultry, on="folio", how="left")
    adults["owns_poultry"] = adults["owns_poultry"].fillna(0).astype(int)

    # If no adults match criteria, return empty with expected columns
    if adults.empty:
        return pd.DataFrame({"owns_poultry": [], "average_age": [], "num_adults_older_than_overall_mean": []})

    # Overall mean age across the selected adults
    overall_mean_age = adults["edad"].mean()

    # Indicator for adults older than overall mean
    adults["older_than_overall_mean"] = adults["edad"] > overall_mean_age

    # Aggregate by poultry ownership
    result = (
        adults.groupby("owns_poultry", as_index=False)
        .agg(
            average_age=("edad", "mean"),
            num_adults_older_than_overall_mean=("older_than_overall_mean", "sum"),
        )
        .sort_values("owns_poultry")
        .reset_index(drop=True)
    )

    return result