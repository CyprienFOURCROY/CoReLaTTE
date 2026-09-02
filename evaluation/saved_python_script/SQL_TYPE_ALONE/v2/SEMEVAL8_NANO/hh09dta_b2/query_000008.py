def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    ah = tables["ii_ah"]
    
    # Filter households that own a motor vehicle (ah03d == 1)
    # and have reported debt values (crh04_1 != 8)
    ah_motor_vehicle = ah[ah["ah03d"] == 1]
    crh_debt_reported = crh[crh["crh04_1"] != 8]
    
    # Merge households with their debt info on 'folio'
    merged = pd.merge(ah_motor_vehicle, crh_debt_reported, on="folio", how="inner")
    
    # Filter households with reported debt value (crh04_1 != 8)
    households_with_debt = merged[merged["crh04_1"] != 8]
    
    # Calculate total household debt (including interest)
    # Drop rows with NaN in 'crh04_2' (debt value)
    households_with_debt = households_with_debt.dropna(subset=["crh04_2"])
    # Compute total debt
    households_with_debt = households_with_debt.assign(total_debt=households_with_debt["crh04_2"])
    
    # Merge with portad to get 'ent' (state)
    households_with_debt = pd.merge(households_with_debt, portad[["folio", "ent"]], on="folio", how="left")
    
    # Map 'ent' codes to state names (optional, not necessary for ranking)
    # Calculate overall average total debt
    overall_avg_debt = households_with_debt["total_debt"].mean()
    
    # Calculate average total debt per state
    state_debt_avg = (
        households_with_debt.groupby("ent")["total_debt"]
        .mean()
        .reset_index()
        .rename(columns={"ent": "state_code", "total_debt": "avg_debt"})
    )
    
    # Filter states where average debt exceeds overall average
    high_debt_states = state_debt_avg[state_debt_avg["avg_debt"] > overall_avg_debt]
    
    # Get top 10 states with highest average debt
    top_states = (
        high_debt_states.sort_values(by="avg_debt", ascending=False)
        .head(10)
        .merge(portad[["ent"]].drop_duplicates(), left_on="state_code", right_on="ent", how="left")
    )
    
    # Return state codes and their average debts
    result = top_states[["state_code", "avg_debt"]]
    return result