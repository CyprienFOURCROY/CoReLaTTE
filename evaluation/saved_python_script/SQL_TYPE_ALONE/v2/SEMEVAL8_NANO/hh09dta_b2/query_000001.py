def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    vlh = tables["ii_vlh"]
    
    # Filter households that answered "Yes" to knowing a family or friend robbed in the last 5 years
    se_filtered = se[se["se05_1a"] == 1]
    
    # Merge with portad to get state info
    merged = pd.merge(se_filtered[["folio"]], portad[["folio", "ent"]], on="folio", how="inner")
    
    # Count households per state with at least 5 households answering Yes
    household_counts = merged.groupby("ent").size()
    states_with_min_households = household_counts[household_counts >= 5].index
    
    # Filter merged to only include these states
    merged_states = merged[merged["ent"].isin(states_with_min_households)]
    
    # Merge with vlh to get "Feel safe at home?" and "Leave lights on as a security method?"
    vlh_relevant = vlh[["folio", "vlh04", "vlh06"]]
    full_data = pd.merge(merged_states, vlh_relevant, on="folio", how="left")
    
    # Map state codes to descriptive labels (optional, not required for output)
    # Compute mean responses for each state
    result = (
        full_data.groupby("ent")
        .agg(
            avg_feel_safe=("vlh04", "mean"),
            avg_leave_lights=("vlh06", "mean"),
            household_count=("folio", "count")
        )
        .reset_index()
    )
    
    # Order from safest to least safe based on "Feel safe at home?" (lower means less safe)
    result = result.sort_values(by="avg_feel_safe", ascending=True)
    
    # Select only relevant columns
    result = result[["ent", "avg_feel_safe", "avg_leave_lights", "household_count"]]
    
    return result