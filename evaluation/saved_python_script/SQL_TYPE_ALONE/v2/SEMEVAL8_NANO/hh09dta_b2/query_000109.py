def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    ah = tables["ii_ah"]
    inr = tables["ii_inr"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Identify households with at least one member aged 25-54
    age_mask = (oaxaca_households["edad"] >= 25) & (oaxaca_households["edad"] <= 54)
    households_with_25_54 = oaxaca_households[age_mask]["folio"].unique()
    
    # Filter households with at least one member owning financial assets/afores (ah03h == 1)
    ah_filtered = ah[ah["ah03h"] == 1]
    households_with_assets = ah_filtered["folio"].unique()
    
    # Find intersection: households in Oaxaca with 25-54 and with assets
    target_households = set(households_with_25_54).intersection(set(households_with_assets))
    
    # Filter crh for these households
    crh_target = crh[crh["folio"].isin(target_households)]
    
    # Filter crh for recorded total debts + interests (crh04_1 == 1)
    crh_debt_recorded = crh_target[crh_target["crh04_1"] == 1]
    
    # Compute average total debts + interests
    avg_debt = crh_debt_recorded["crh04_2"].mean()
    
    # Filter crh for households with total debts + interests higher than the average
    crh_high_debt = crh_debt_recorded[crh_debt_recorded["crh04_2"] > avg_debt]
    
    # Get the set of households with high debts
    households_high_debt = crh_high_debt["folio"].unique()
    
    # Count households in Oaxaca with at least one member aged 25-54, with assets, and high debt
    count = sum(
        1 for folio in households_high_debt
        if folio in households_with_25_54 and folio in households_with_assets
    )
    
    return pd.DataFrame({"households_count": [count]})