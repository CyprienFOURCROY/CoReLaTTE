def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]
    
    # Merge portad and in on 'folio'
    merged = pd.merge(df_portad, df_in, on='folio', how='inner')
    # Merge with ah on 'folio' and 'ls'
    merged = pd.merge(merged, df_ah, on=['folio', 'ls'], how='inner')
    
    # Filter households with positive amount received from 'in02a10' (Other Government Program)
    # and where 'in02a10' is not null and > 0
    mask_amount = merged['in02a10'].notnull() & (merged['in02a10'] > 0)
    df_filtered = merged[mask_amount]
    
    # Filter households with at least one member owning an electronic device
    # 'ah04e_1' indicates value of electronic device ownership
    mask_electronic = merged['ah04e_1'].notnull() & (merged['ah04e_1'] == 1)
    df_electronic = merged[mask_electronic]
    
    # Find household IDs with at least one member owning an electronic device
    households_with_electronic = set(df_electronic['folio'])
    
    # Filter the main dataframe to include only households with at least one member owning an electronic device
    df_final = df_filtered[df_filtered['folio'].isin(households_with_electronic)]
    
    # Group by 'ent' (state)
    group = df_final.groupby('ent')
    
    # Calculate number of households per state with at least one member owning an electronic device
    households_count = group['folio'].nunique()
    # Calculate average 'in02a10' per state
    avg_amount = group['in02a10'].mean()
    
    # Filter states with at least 30 such households and average > 2000
    result = pd.DataFrame({
        'households_count': households_count,
        'average_amount': avg_amount
    }).reset_index()
    result = result[(result['households_count'] >= 30) & (result['average_amount'] > 2000)]
    
    # Order from highest to lowest average
    result = result.sort_values(by='average_amount', ascending=False)
    
    # Select only 'ent' and 'average_amount' columns
    result = result[['ent', 'average_amount']]
    
    # Rename 'ent' to 'state' for clarity
    # Map 'ent' codes to state names if needed (not specified), so keep as is
    return result.reset_index(drop=True)