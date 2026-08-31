def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    vlh = tables["ii_vlh"]
    
    # Filter households that answered "Yes" to knowing a family or friend robbed house/business in last 5 years
    se_filtered = se[se["se02ea_1"] == 1]
    
    # Count households per state (ent)
    households_per_state = portad.groupby("ent")["folio"].nunique().reset_index(name="household_count")
    
    # Filter states with at least 5 households answering Yes
    states_with_min_households = households_per_state[households_per_state["household_count"] >= 5]["ent"]
    
    # Filter households that know a family/friend robbed house in last 5 years and belong to these states
    households_in_states = portad[portad["ent"].isin(states_with_min_households)]
    households_in_states = households_in_states.merge(se_filtered, on="folio", how="inner")
    
    # Get list of folios in these households
    folios_in_states = households_in_states["folio"].unique()
    
    # Filter vlh data for these folios
    vlh_filtered = vlh[vlh["folio"].isin(folios_in_states)]
    
    # Calculate average responses for "Feel safe at home?" (vlh04) and "Leave lights on as a security method?" (vlh06)
    # Exclude NaN values in the mean calculation
    avg_vlh04 = vlh_filtered["vlh04"].mean()
    avg_vlh06 = vlh_filtered["vlh06"].mean()
    
    # Prepare the result DataFrame
    result = pd.DataFrame({
        "ent": [int(e) for e in states_with_min_households],
        "household_count": [int(h) for h in households_per_state.set_index("ent").loc[states_with_min_households]["household_count"]],
        "avg_feel_safe": [avg_vlh04],
        "avg_leave_lights": [avg_vlh06]
    })
    
    # Order by "Feel safe at home?" (vlh04) from safest (lowest) to least safe (highest)
    result_sorted = result.sort_values(by="avg_feel_safe", ascending=True).reset_index(drop=True)
    
    return result_sorted