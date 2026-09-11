def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    ah = tables["ii_ah"]
    crh = tables["ii_crh"]
    
    # Filter for Oaxaca (ent == 20)
    oaxaca_portad = portad[portad["ent"] == 20]
    
    # Merge portad with inr on 'folio'
    merged_inr = pd.merge(oaxaca_portad, inr, on="folio", how="left")
    
    # Merge with ah on 'folio' and 'ls'
    merged_ah = pd.merge(merged_inr, ah, on=["folio", "ls"], how="left")
    
    # Merge with crh on 'folio'
    merged_crh = pd.merge(merged_ah, crh, on="folio", how="left")
    
    # Filter for adults (edad >= 18)
    adults = merged_crh[merged_crh["edad"] >= 18]
    
    # Filter for households that own a motor vehicle (ah03d == 1)
    households_with_vehicle = adults[adults["ah03d"] == 1]
    
    # Calculate the average total debts plus interest among Oaxaca households with reported values
    # First, filter for households with reported total debts (crh04_1 == 1 or 8)
    households_debt_reported = households_with_vehicle[
        (households_with_vehicle["crh04_1"] == 1) | (households_with_vehicle["crh04_1"] == 8)
    ]
    
    # Compute the mean of total debts + interests (crh04_2) for these households
    mean_debt = households_debt_reported["crh04_2"].mean()
    
    # Filter households where total debts + interests exceed the average
    households_exceed = households_with_vehicle[
        (households_with_vehicle["crh04_2"] > mean_debt)
    ]
    
    # Count unique households (by 'folio') in this filtered set
    count_households = households_exceed["folio"].nunique()
    
    # Prepare the result as a DataFrame
    return pd.DataFrame(
        {"count": [count_households]}
    )