def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    in_table = tables["ii_in"]
    
    # Merge portad and in_table on 'folio'
    merged = pd.merge(portad, in_table, on='folio', how='inner')
    
    # Filter individuals older than overall average age
    overall_avg_age = merged['edad'].mean()
    age_filtered = merged[merged['edad'] > overall_avg_age]
    
    # Filter households with positive total debts + interests
    debt_filtered = age_filtered[age_filtered['crh04_1'] == 1]
    debt_filtered = debt_filtered[debt_filtered['crh04_2'] > 0]
    
    # Group by 'ent' (state) and compute mean of 'crh04_2' and count of individuals
    result = debt_filtered.groupby('ent').agg(
        avg_debt=('crh04_2', 'mean'),
        count=('folio', 'count')
    ).reset_index()
    
    # Select top 5 states with highest average debt
    top5 = result.nlargest(5, 'avg_debt')
    
    # Map 'ent' codes to state names for clarity (optional, not required)
    # But since only codes are provided, return as is.
    
    return top5[['ent', 'avg_debt', 'count']]