def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    ah = tables["ii_ah"]
    
    # Filter households with at least 20 households owning a motor vehicle
    # Step 1: Filter households owning a motor vehicle (ah03d == 1)
    ah_motor_vehicle = ah[ah["ah03d"] == 1][["folio"]]
    # Count number of households per state
    # Merge with portad to get 'ent' (state)
    ah_motor_vehicle = ah_motor_vehicle.merge(portad[["folio", "ent"]], on="folio", how="left")
    # Count households per state
    households_per_state = ah_motor_vehicle.groupby("ent").size().reset_index(name="household_count")
    # Filter states with at least 20 households owning a motor vehicle
    states_with_20plus = households_per_state[households_per_state["household_count"] >= 20]["ent"]
    
    # Filter portad for these states
    portad_filtered = portad[portad["ent"].isin(states_with_20plus)]
    
    # For these households, get 'folio' and 'ent'
    households_in_states = portad_filtered[["folio", "ent"]]
    
    # Step 2: For these households, determine if they use a plot of land for farming/vegetable (su01 == 1)
    su_filtered = su[su["folio"].isin(households_in_states["folio"])]
    land_use = su_filtered[["folio", "su01"]]
    land_use = land_use.drop_duplicates(subset=["folio"])
    land_use = land_use.rename(columns={"su01": "uses_land"})
    
    # Merge with households_in_states to get state info
    households_land = households_in_states.merge(land_use, on="folio", how="left")
    
    # Replace NaN in 'uses_land' with 3 (No) assuming missing means no land use
    households_land["uses_land"] = households_land["uses_land"].fillna(3)
    
    # Step 3: Calculate the average number of households that use land per state
    land_use_stats = households_land.groupby("ent")["uses_land"].apply(
        lambda x: (x == 1).sum()
    ).reset_index(name="land_users_count")
    
    # Calculate total households per state (already have from earlier)
    total_households = households_per_state.set_index("ent")["household_count"]
    
    # Merge to get total households per state
    land_use_stats = land_use_stats.set_index("ent")
    land_use_stats["total"] = total_households
    # Compute proportion of land users
    land_use_stats["prop_land_users"] = land_use_stats["land_users_count"] / land_use_stats["total"]
    
    # Compute overall average proportion
    overall_avg = land_use_stats["prop_land_users"].mean()
    
    # Select states with above-average land use
    states_above_avg = land_use_stats[land_use_stats["prop_land_users"] > overall_avg].reset_index()
    
    # Prepare final output: list of states (ent) with above-average land use among households owning a motor vehicle
    result = states_above_avg[["ent"]]
    
    return result