def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    in_table = tables["ii_in"]
    
    # Filter households that received Liconsa milk in last 12 months
    in_liconsa = in_table[in_table["in03a"] == 1]
    
    # Merge portad with in_table on 'folio'
    merged = pd.merge(portad, in_liconsa[["folio"]], on="folio", how="inner")
    
    # Identify households with at least one senior (edad >=70) and at least one child (edad <12)
    # For each household, check if it has both
    household_groups = merged.groupby("folio")
    
    # For each household, check conditions
    def household_has_both(group):
        has_senior = (group["edad"] >= 70).any()
        has_child = (group["edad"] < 12).any()
        return has_senior and has_child
    
    households_both = household_groups.filter(household_has_both)
    
    # Count households per 'ent' (state)
    count_per_state = (
        pd.merge(households_both, portad[["folio", "ent"]], on="folio", how="left")
        .groupby("ent")
        .size()
        .reset_index(name="household_count")
    )
    
    # Calculate the overall average number of such households across all states
    total_households_both = len(households_both)
    total_states = portad["ent"].nunique()
    overall_avg = total_households_both / total_states if total_states > 0 else 0
    
    # Filter states with above-average number
    above_avg_states = count_per_state[count_per_state["household_count"] > overall_avg]
    
    # Map 'ent' codes to state names (optional, but not required for output)
    # For clarity, include state code as is
    result = above_avg_states[["ent", "household_count"]]
    result.columns = ["state_code", "households"]
    
    return result