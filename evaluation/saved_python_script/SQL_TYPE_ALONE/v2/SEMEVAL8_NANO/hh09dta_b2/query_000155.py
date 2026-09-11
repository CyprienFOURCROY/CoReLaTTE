def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    crh = tables["ii_crh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge household info with ah and crh on folio and ls
    merged = oaxaca_households.merge(ah, on=["folio", "ls"], how="left")
    merged = merged.merge(crh, on=["folio"], how="left")
    
    # Filter households with at least one member owning a motor vehicle (ah03d == 1)
    has_motor_vehicle = merged[merged["ah03d"] == 1]
    
    # Filter households with at least one member owning financial assets/afores (ah03h == 1)
    has_financial_assets = merged[merged["ah03h"] == 1]
    
    # Find intersection: households satisfying both conditions
    households_meeting_conditions = pd.merge(
        has_motor_vehicle[["folio"]],
        has_financial_assets[["folio"]],
        on="folio"
    )["folio"].unique()
    
    # Filter original merged data for these households
    filtered = merged[merged["folio"].isin(households_meeting_conditions)]
    
    # For these households, get total debts + interests (crh04_1 == 1)
    relevant_crh = crh[
        (crh["folio"].isin(households_meeting_conditions)) &
        (crh["crh04_1"] == 1)
    ]
    
    # Calculate average total debts plus interest in pesos
    avg_debt = relevant_crh["crh04_2"].mean()
    
    # Return as DataFrame
    return pd.DataFrame(
        {"average_total_debts_plus_interest": [avg_debt]}
    )