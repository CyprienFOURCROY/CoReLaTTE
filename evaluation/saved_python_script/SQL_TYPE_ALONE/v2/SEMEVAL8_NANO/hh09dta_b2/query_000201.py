def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    crh = tables["ii_crh"]
    
    # Filter households with total debts + interests reported (crh04_1 == 1)
    crh_debt = crh[crh["crh04_1"] == 1]
    # Count households per state (ent)
    debt_counts = crh_debt.groupby("folio").size().reset_index(name="debt_count")
    
    # Merge with portad to get state info
    portad_debt = portad.merge(debt_counts, on="folio", how="inner")
    
    # Filter households with at least one member owning electronic device (ah04e_1 == 1)
    ah_electronic = ah[ah["ah04e_1"] == 1]
    # Count households with electronic devices
    electronic_counts = ah_electronic.groupby("folio").size().reset_index(name="electronic_count")
    
    # Merge with portad to get household info
    portad_electronic = portad.merge(electronic_counts, on="folio", how="inner")
    
    # For each state, count households that meet both conditions
    # Merge debt and electronic data on folio
    merged = portad_debt.merge(portad_electronic[["folio", "ent"]], on="folio", how="inner")
    
    # Count households per state that satisfy both conditions
    state_counts = merged.groupby("ent").size().reset_index(name="count")
    
    # Calculate the average count across states
    avg_count = state_counts["count"].mean()
    
    # Filter states with count >= average
    result = state_counts[state_counts["count"] >= avg_count]
    
    # Map state codes to labels if needed (optional), here we keep codes
    # Return the result
    return result[['ent', 'count']]