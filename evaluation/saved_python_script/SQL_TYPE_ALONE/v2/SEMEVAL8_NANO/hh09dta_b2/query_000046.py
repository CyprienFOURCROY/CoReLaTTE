def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    in_table = tables["ii_in"]
    vhl = tables["ii_vlh"]
    
    # Merge portad with in_table on 'folio'
    df = portad.merge(in_table, on='folio', how='inner')
    # Merge with vhl on 'folio'
    df = df.merge(vhl, on='folio', how='inner')
    
    # Filter households with positive 'in02a12' (amount received directly from Other Government Program)
    df_pos = df[df['in02a12'] > 0]
    
    # For households with 'in02a12' > 0, compute total robberies since 2005
    # 'vlh13' is total times robbed in HH since 2005
    # Filter households with at least 30 such households
    household_counts = df_pos.groupby('ent').size()
    valid_states = household_counts[household_counts >= 30].index
    
    # Filter data for these states
    df_filtered = df_pos[df_pos['ent'].isin(valid_states)]
    
    # Group by state and compute count and mean of 'vlh13'
    result = (
        df_filtered.groupby('ent')
        .agg(
            household_count=('folio', 'nunique'),
            avg_robberies_since_2005=('vlh13', 'mean')
        )
        .reset_index()
    )
    
    # Filter states with average robberies > overall average among households with positive 'in02a12'
    overall_mean = df_pos['vlh13'].mean()
    result = result[result['avg_robberies_since_2005'] > overall_mean]
    
    # Map 'ent' codes to state names (optional, if needed)
    # For clarity, include state names
    state_map = {
        2: 'Baja California',
        3: 'Baja California Sur',
        4: 'Campeche',
        5: 'Coahuila',
        6: 'Colima',
        7: 'Chiapas',
        9: 'Distrito Federal',
        10: 'Durango',
        11: 'Guanajuato',
        12: 'Guerrero',
        13: 'Hidalgo',
        14: 'Jalisco',
        15: 'Estado de México',
        16: 'Michoacán',
        17: 'Morelos',
        18: 'Nayarit',
        19: 'Nuevo León',
        20: 'Oaxaca',
        21: 'Puebla',
        22: 'Querétaro',
        25: 'Sinaloa',
        26: 'Sonora',
        28: 'Tamaulipas',
        29: 'Tlaxcala',
        30: 'Veracruz',
        31: 'Yucatán',
        32: 'Zacatecas'
    }
    result['state'] = result['ent'].map(state_map)
    result = result[['state', 'household_count', 'avg_robberies_since_2005']]
    return result