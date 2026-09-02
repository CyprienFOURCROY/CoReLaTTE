def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    
    # Merge portad with crh on 'folio'
    merged = pd.merge(portad, crh, on='folio', how='inner')
    
    # Filter out records where 'crh04_2' (total debts + interests in pesos) is missing
    debt_data = merged[merged['crh04_2'].notna()].copy()
    
    # Calculate overall average of 'crh04_2' (total debts + interests)
    overall_avg = debt_data['crh04_2'].mean()
    
    # Group by 'ent' (state), compute mean and count
    state_group = debt_data.groupby('ent').agg(
        avg_debt=('crh04_2', 'mean'),
        household_count=('folio', 'count')
    ).reset_index()
    
    # Filter states with average debt greater than overall average
    filtered_states = state_group[state_group['avg_debt'] > overall_avg]
    
    # Sort from highest to lowest average debt
    result = filtered_states.sort_values(by='avg_debt', ascending=False)
    
    # Select relevant columns and rename 'ent' to 'state'
    result = result[['ent', 'avg_debt', 'household_count']]
    result = result.rename(columns={'ent': 'state', 'avg_debt': 'average_debt', 'household_count': 'household_count'})
    
    return result