def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    se = tables["ii_se"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Filter households with at least one member aged 60 or older
    aged_60_plus = oaxaca_households[oaxaca_households["edad"] >= 60]
    households_with_60_plus = aged_60_plus["folio"].unique()
    
    # Filter households with at least one member younger than 30
    under_30 = oaxaca_households[oaxaca_households["edad"] < 30]
    households_with_under_30 = under_30["folio"].unique()
    
    # Find households that satisfy both conditions
    target_households = set(households_with_60_plus).intersection(set(households_with_under_30))
    
    # Filter households in the target set
    filtered_portad = oaxaca_households[oaxaca_households["folio"].isin(target_households)]
    
    # Get households with any indebtedness (crh02_1 == 1)
    crh_indebted = crh[crh["folio"].isin(filtered_portad["folio"])]
    indebted_mask = crh_indebted["crh02_1"] == 1
    indebted_crh = crh_indebted[indebted_mask]
    
    # Calculate Oaxaca-wide average total debts + interests among indebted households
    # Drop NaNs in crh04_2
    indebted_crh_clean = indebted_crh.dropna(subset=["crh04_2"])
    if len(indebted_crh_clean) == 0:
        average_debt = 0
    else:
        average_debt = indebted_crh_clean["crh04_2"].mean()
    
    # Filter households with total debt >= Oaxaca-wide average
    households_meeting_debt_threshold = set(
        indebted_crh[indebted_crh["crh04_2"] >= average_debt]["folio"]
    )
    
    # Filter households in the target set that meet the debt condition
    final_households = set(target_households).intersection(households_meeting_debt_threshold)
    
    # For these households, get total debts + interests
    crh_final = crh[crh["folio"].isin(final_households)]
    crh_final_clean = crh_final.dropna(subset=["crh04_2"])
    
    # Compute the average total debts + interests
    if len(crh_final_clean) == 0:
        avg_total_debt = 0
    else:
        avg_total_debt = crh_final_clean["crh04_2"].mean()
    
    return pd.DataFrame({"average_total_debt": [avg_total_debt]})