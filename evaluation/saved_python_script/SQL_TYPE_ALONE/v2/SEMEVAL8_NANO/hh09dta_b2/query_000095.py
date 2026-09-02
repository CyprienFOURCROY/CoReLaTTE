def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    ah = tables["ii_ah"]
    se = tables["ii_se"]
    se_enriched = tables["ii_se_enriched"]
    ah_enriched = tables["ii_ah_enriched"]
    
    # Filter households that reported producing or selling fattening animals in last 12 months
    fattening_mask = inr["inr02j"] == 1
    households_fattening = inr.loc[fattening_mask, "folio"].unique()
    
    # Subset inr to these households
    inr_fattening = inr[inr["folio"].isin(households_fattening)]
    
    # Calculate average bull/cow asset value among these households
    # First, get the asset value for bull/cow
    ah_bull_cow = ah_enriched[ah_enriched["folio"].isin(households_fattening)]
    # Filter for households that own bull/cow (value == 1)
    bull_cow_mask = ah_bull_cow["ah04j_1"] == 1
    ah_bull_cow_own = ah_bull_cow[bull_cow_mask]
    # Compute mean value of the asset among these households
    # Note: The value columns are "ah04j_2" for the value
    # For households owning bull/cow, get their asset value
    asset_values = ah_bull_cow_own["ah04j_2"]
    # Exclude NaNs
    asset_values = asset_values.dropna()
    if len(asset_values) == 0:
        # No households with bull/cow asset value reported
        return pd.DataFrame({"average_adults": [0.0]})
    avg_asset_value = asset_values.mean()

    # Filter households that own bull/cow and have asset value > average
    households_with_bull_cow = ah_bull_cow[
        (ah_bull_cow["ah04j_1"] == 1) & (ah_bull_cow["ah04j_2"] > avg_asset_value)
    ]["folio"].unique()

    # For these households, find all individuals aged 18+
    portad_filtered = portad[portad["folio"].isin(households_with_bull_cow)]
    adults = portad_filtered[portad_filtered["edad"] >= 18]
    # Count number of adults per household
    adults_per_household = adults.groupby("folio").size()

    # Compute the average number of adults per household
    if len(adults_per_household) == 0:
        average_adults = 0.0
    else:
        average_adults = adults_per_household.mean()

    return pd.DataFrame({"average_adults": [average_adults]})