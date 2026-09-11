def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    se = tables["ii_se"]
    
    # Filter households with at least one adult (edad >= 18)
    adults = portad[portad["edad"] >= 18]
    households_with_adults = adults["folio"].unique()
    
    # Filter inr for households that produced or sold meat in last 12 months (inr02c == 1)
    inr_meat = inr[(inr["folio"].isin(households_with_adults)) & (inr["inr02c"] == 1)]
    households_meat = inr_meat["folio"].unique()
    
    # Filter se for households that experienced disease/accident/hospitalization in last 5 years (se01b == 1)
    se_disease = se[(se["folio"].isin(households_meat)) & (se["se01b"] == 1)]
    households_disease = se_disease["folio"].unique()
    
    # Count households per state with at least one adult, that produced/sold meat, and experienced disease
    # Merge portad with households_disease to get state info
    portad_filtered = portad[portad["folio"].isin(households_disease)]
    
    # Count households per state
    count_per_state = (
        portad_filtered.groupby("ent")["folio"]
        .nunique()
        .reset_index()
        .rename(columns={"folio": "household_count"})
    )
    
    # Calculate the average count across all states
    avg_count = count_per_state["household_count"].mean()
    
    # Select states with count >= average
    result = count_per_state[count_per_state["household_count"] >= avg_count]
    
    # Map state codes to state names (optional, only if needed)
    # For clarity, include state code as 'state_code'
    result = result.rename(columns={"ent": "state_code"})
    
    # Return the result with state_code and count
    return result[["state_code", "household_count"]]