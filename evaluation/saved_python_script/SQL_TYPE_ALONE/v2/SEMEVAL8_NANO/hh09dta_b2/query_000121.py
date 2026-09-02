def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    
    # Filter households where household member owns a motor vehicle
    # and reports feeling safe or very safe at home
    # Conditions:
    # ah03d (owns motor vehicle) == 1
    # vlh04 (feels safe at home) in [1, 2]
    
    # Merge household data with household member data on 'folio'
    merged = pd.merge(df_portad, df_ah, on='folio', how='inner')
    
    # Filter for ownership of motor vehicle
    owns_motor_vehicle = merged['ah03d'] == 1
    
    # Filter for feeling safe or very safe
    safe_at_home = merged['vlh04'].isin([1, 2])
    
    # Combined filter
    filtered = merged[owns_motor_vehicle & safe_at_home]
    
    # Group by 'ent' (state) and count unique households
    result = (
        filtered.groupby('ent')
        .agg(households=('folio', 'nunique'))
        .reset_index()
    )
    
    # Filter states with at least 100 such households
    result = result[result['households'] >= 100]
    
    # Sort by count descending
    result = result.sort_values(by='households', ascending=False)
    
    # Rename columns for clarity
    result = result.rename(columns={'ent': 'state_code'})
    
    return result[['state_code', 'households']]