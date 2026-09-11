def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    su = tables["ii_su"]
    
    # Filter households that use a plot/land for farming
    # su01 == 1 indicates household uses land for farming
    farming_hh = su[su["su01"] == 1]
    
    # Get household IDs of farming households
    farming_folios = farming_hh["folio"].unique()
    
    # Filter crh for these households with recorded total debt (crh04_1 != 8)
    # and debt amount (crh04_2) not null
    crh_farming = crh[
        (crh["folio"].isin(farming_folios)) &
        (crh["crh04_1"] != 8) &
        (crh["crh04_2"].notna())
    ]
    
    # Compute overall average debt (crh04_2) for these households
    overall_avg_debt = crh_farming["crh04_2"].mean()
    
    # Filter households with debt exceeding the overall average
    high_debt = crh_farming[crh_farming["crh04_2"] > overall_avg_debt]
    
    # Merge with portad to get state information
    merged = high_debt.merge(portad[["folio", "ent"]], on="folio", how="left")
    
    # Group by state (ent) and compute mean debt
    state_debt = (
        merged.groupby("ent")["crh04_2"]
        .mean()
        .reset_index()
        .rename(columns={"crh04_2": "avg_debt"})
    )
    
    # Filter states with average debt > 10,000
    result = state_debt[state_debt["avg_debt"] > 10000]
    
    # Merge with portad to get state names if needed (optional)
    # For now, return state code and average debt
    return result[['ent', 'avg_debt']]