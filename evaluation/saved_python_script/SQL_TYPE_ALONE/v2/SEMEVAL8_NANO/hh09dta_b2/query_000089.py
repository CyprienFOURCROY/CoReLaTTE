def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    ah = tables["ii_ah"]
    
    # Filter households that own a motor vehicle (ah03d == 1)
    households_with_vehicle = ah[ah["ah03d"] == 1][["folio"]]
    
    # Filter individuals aged 25 or older
    individuals_25_plus = portad[portad["edad"] >= 25][["folio", "edad"]]
    
    # Merge individuals with households owning a vehicle
    individuals_in_vehicle_households = pd.merge(
        individuals_25_plus,
        households_with_vehicle,
        on="folio",
        how="inner"
    )
    
    # Filter individuals in these households
    individuals_in_households_with_vehicle = individuals_in_vehicle_households
    
    # Filter crh for these households
    crh_filtered = crh[crh["folio"].isin(individuals_in_households_with_vehicle["folio"])]
    
    # Compute total debts + interests (crh04_2)
    # Filter for recorded values (not NaN)
    crh_debts = crh_filtered[crh_filtered["crh04_2"].notna()]
    
    # Calculate overall average household amount paid on debts
    household_debt_sums = crh_debts.groupby("folio")["crh04_2"].sum()
    overall_avg_debt = household_debt_sums.mean()
    
    # Select households with recorded total debts
    households_with_debt_recorded = household_debt_sums.index
    
    # Filter households with total debts > overall average
    households_above_avg_debt = household_debt_sums[household_debt_sums > overall_avg_debt].index
    
    # Filter individuals in these households
    individuals_in_above_avg_households = individuals_in_households_with_vehicle[
        individuals_in_households_with_vehicle["folio"].isin(households_above_avg_debt)
    ]
    
    # Filter for individuals aged 25 or older
    final_individuals = individuals_in_above_avg_households[individuals_in_above_avg_households["edad"] >= 25]
    
    # Compute the average age
    avg_age = final_individuals["edad"].mean()
    
    return pd.DataFrame({"average_age": [avg_age]})