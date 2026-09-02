def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    in_table = tables["ii_in"]
    
    # Filter adults (age >= 18)
    adults = portad[portad["edad"] >= 18]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca_adults = adults[adults["ent"] == 15]
    
    # Merge with household info from vlh and in tables
    merged = oaxaca_adults.merge(vlh[["folio", "vlh03", "vlh12c"]], on="folio", how="left")
    merged = merged.merge(in_table[["folio", "in01a2_1", "in01a2_2"]], on="folio", how="left")
    
    # Filter individuals living in households that report feeling unsafe or very unsafe
    unsafe_mask = merged["vlh04"].isin([3, 4])  # 3: Unsafe, 4: Very unsafe
    unsafe_households = merged[unsafe_mask]
    
    # Calculate household average of total forced break-ins since 2005
    # First, filter households with reported break-ins since 2005
    break_in_mask = unsafe_households["vlh12c"] == 1  # 1: Entered force rob in HH since 2005
    households_breakins = unsafe_households[break_in_mask]
    
    # Group by household and count total break-ins since 2005
    household_breakins = households_breakins.groupby("folio")["vlh13a"].sum(min_count=1).reset_index()
    household_breakins.rename(columns={"vlh13a": "total_breakins_since_2005"}, inplace=True)
    
    # Compute average total break-ins across all households with feeling unsafe
    avg_breakins = household_breakins["total_breakins_since_2005"].mean()
    
    # Merge back to filter individuals in households above the average
    final = households_breakins[household_breakins["total_breakins_since_2005"] > avg_breakins]
    # Get list of household folios above average
    folios_above_avg = final["folio"]
    
    # Filter individuals who live in these households
    result = unsafe_households[unsafe_households["folio"].isin(folios_above_avg)]
    
    # Select relevant columns for output
    output = result[["folio", "ls", "edad"]]
    
    return output