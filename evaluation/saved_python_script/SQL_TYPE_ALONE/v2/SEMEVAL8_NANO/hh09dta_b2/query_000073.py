def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    
    # Filter households that received Liconsa milk in the last 12 months
    df_in_liconsa = df_in[df_in["in03a"] == 1]
    
    # Merge with portad to get state info
    merged = pd.merge(df_in_liconsa[["folio"]]], df_portad[["folio", "ent"]], on="folio", how="inner")
    
    # Filter households that feel unsafe or very unsafe at home
    # 'vlh04' column in 'ii_vlh' indicates feeling safe at home
    # Values: 3 (Unsafe), 4 (Very unsafe)
    # Merge with 'ii_vlh' to get 'vlh04' info
    df_vlh = tables["ii_vlh"]
    merged = pd.merge(merged, df_vlh[["folio", "vlh04"]], on="folio", how="inner")
    
    # Keep only households with 'vlh04' == 3 or 4
    unsafe_households = merged[merged["vlh04"].isin([3, 4])]
    
    # Count number of such households per state
    counts = unsafe_households.groupby("ent").size().reset_index(name="count")
    
    # Calculate cross-state average
    avg_count = counts["count"].mean()
    
    # Filter states with counts >= average
    filtered_counts = counts[counts["count"] >= avg_count]
    
    # Get top five states by count
    top_five = filtered_counts.nlargest(5, "count")
    
    # Map 'ent' codes to state names (if needed), but only codes are provided
    # Return the state code and count
    result = top_five[["ent", "count"]]
    result.columns = ["state_code", "household_count"]
    
    return result