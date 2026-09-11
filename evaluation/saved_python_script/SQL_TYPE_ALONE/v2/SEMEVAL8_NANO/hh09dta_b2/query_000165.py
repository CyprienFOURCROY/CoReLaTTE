def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    se = tables["ii_se"]
    
    # Filter households with disease/accident/hospitalization in last 5 years
    # se01b indicates disease/accident/hospital HHM? (1=Yes, 3=No)
    se_disease_mask = se["se01b"] == 1
    
    # Filter households with at least one adult (age >= 18)
    # portad['edad'] is age, filter for age >= 18
    adults_mask = portad["edad"] >= 18
    
    # Filter households with reported total debts plus interest (crh['crh04_2'] not null)
    # crh['crh04_2'] is total debts + interests in pesos
    debt_mask = crh["crh04_2"].notna()
    
    # Combine all filters
    combined_mask = se_disease_mask & adults_mask & debt_mask
    
    # Filter tables accordingly
    households_filtered = portad[combined_mask]
    folios = households_filtered["folio"]
    
    # Filter crh for these households
    crh_filtered = crh[crh["folio"].isin(folios)]
    # Keep only households with non-null total debts
    crh_filtered = crh_filtered[crh_filtered["crh04_2"].notna()]
    
    # Calculate overall average total debt
    overall_avg_debt = crh_filtered["crh04_2"].mean()
    
    # Prepare data for households with debt > overall average
    high_debt_mask = crh_filtered["crh04_2"] > overall_avg_debt
    high_debt_households = crh_filtered[high_debt_mask]
    
    # Merge with households to get demographic info
    merged = households_filtered.merge(high_debt_households[["folio", "crh04_2"]], on="folio", how="inner")
    
    # Merge with 'nna' to get non-ag business ownership info
    merged = merged.merge(nna, on="folio", how="left")
    # Merge with 'portad' to get 'ent' (state)
    merged = merged.merge(portad[["folio", "ent"]], on="folio", how="left")
    
    # Map 'ent' to state name or code if needed (not required for output, only for grouping)
    # Group by state ('ent') and non-ag business ownership ('nna01')
    result = (
        merged.groupby(["ent", "nna01"])
        .agg(
            average_debt=("crh04_2", "mean"),
            households_count=("folio", "nunique")
        )
        .reset_index()
    )
    
    # Rename columns for clarity
    result = result.rename(columns={
        "ent": "state_code",
        "nna01": "nna_business",
        "average_debt": "avg_total_debt",
        "households_count": "num_households"
    })
    
    return result