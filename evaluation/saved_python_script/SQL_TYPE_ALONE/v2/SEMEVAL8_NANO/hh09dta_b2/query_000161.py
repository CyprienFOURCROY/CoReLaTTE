def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    
    # Merge tables on 'folio'
    df_merged = pd.merge(df_portad, df_in, on='folio', how='inner')
    
    # Apply filters:
    # 1. Resident aged 70 or older: 'edad' >= 70
    # 2. Received '70 y más' benefit in last 12 months: 'in01a11_1' == 1
    # 3. Feel unsafe or very unsafe at home: 'vlh04' in [3, 4]
    # 4. Do NOT report knowing a family or friend kidnapped in last 12 months: 'vlh10c' != 1
    
    filtered = df_merged[
        (df_merged['edad'] >= 70) &
        (df_merged['in01a11_1'] == 1) &
        (df_merged['vlh04'].isin([3, 4])) &
        (df_merged['vlh10c'] != 1)
    ]
    
    # Group by 'ent' (state) and count unique households ('folio')
    result = (
        filtered.groupby('ent')['folio']
        .nunique()
        .reset_index(name='household_count')
    )
    
    # Filter states with at least 10 such households
    result = result[result['household_count'] >= 10]
    
    # Sort from highest to lowest
    result = result.sort_values(by='household_count', ascending=False).reset_index(drop=True)
    
    return result