def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_se = tables["ii_se"]
    
    # Filter households that received Liconsa milk in the last 12 months
    df_liconsa = df_in[df_in["in03a"] == 1]
    
    # Merge with portad to get state info
    merged = pd.merge(df_liconsa, df_portad[["folio", "ent"]], on="folio", how="inner")
    
    # Group by state (ent) and count households
    households_per_state = merged.groupby("ent").size()
    
    # Filter states with at least 25 households
    states_with_min_households = households_per_state[households_per_state >= 25].index
    
    # Filter merged data to include only these states
    filtered = merged[merged["ent"].isin(states_with_min_households)]
    
    # Calculate mean of 'in02d' (Amount received directly from Other Government Program) per state
    state_avg = (
        filtered.groupby("ent")["in02d"]
        .mean()
        .rename("avg_in02d")
        .reset_index()
    )
    
    # Calculate overall average across these states
    overall_avg = state_avg["avg_in02d"].mean()
    
    # Select states with average above overall average
    above_avg_states = state_avg[state_avg["avg_in02d"] > overall_avg]
    
    # Map 'ent' codes to state names for clarity (optional, not required)
    # But since only codes are used, we can keep codes or add a mapping if needed.
    
    # Rank states by their average amount received
    ranked = above_avg_states.sort_values(by="avg_in02d", ascending=False).reset_index(drop=True)
    
    # Return the ranking with state code and average
    result = ranked[["ent", "avg_in02d"]]
    result.columns = ["state_code", "average_amount"]
    return result