def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    su = tables["ii_su"]
    
    # Filter for Oaxaca (15) and Puebla (21)
    states_of_interest = [15, 21]
    portad_filtered = portad[portad["ent"].isin(states_of_interest)]
    
    # Merge portad with nna on 'folio'
    merged = pd.merge(portad_filtered, nna, on="folio", how="left")
    
    # Merge with su on 'folio'
    merged = pd.merge(merged, su, on="folio", how="left")
    
    # Create indicator for feeling unsafe or very unsafe at home
    # 'vlh04' codes: 3 (Unsafe), 4 (Very unsafe)
    unsafe_mask = merged["vlh04"].isin([3, 4])
    
    # Household owns/shares non-ag business
    nna_mask = merged["nna01"] == 1
    
    # Does not use plot/land for sowing/farming
    # 'su01' codes: 1 (Yes), 3 (No)
    # We want households where 'su01' == 3 (No)
    land_mask = merged["su01"] == 3
    
    # Apply all conditions
    condition = unsafe_mask & nna_mask & land_mask
    
    # Filter merged DataFrame
    filtered = merged[condition]
    
    # Count households per state
    counts = (
        filtered.groupby("ent")
        .size()
        .reset_index(name="count")
    )
    
    # Get counts for Oaxaca (15) and Puebla (21)
    counts_oaxaca = counts[counts["ent"] == 15]["count"]
    counts_puebla = counts[counts["ent"] == 21]["count"]
    
    # If any state is missing, set count to 0
    count_oaxaca = int(counts_oaxaca.iloc[0]) if not counts_oaxaca.empty else 0
    count_puebla = int(counts_puebla.iloc[0]) if not counts_puebla.empty else 0
    
    # Calculate overall mean across all states in the filtered data
    total_counts = counts["count"].sum()
    total_states = counts["ent"].nunique()
    average_count = total_counts / total_states if total_states > 0 else 0
    
    # Check which of Oaxaca or Puebla are below average
    result_rows = []
    if count_oaxaca < average_count:
        result_rows.append({"state": "Oaxaca", "count": count_oaxaca})
    if count_puebla < average_count:
        result_rows.append({"state": "Puebla", "count": count_puebla})
    
    return pd.DataFrame(result_rows)