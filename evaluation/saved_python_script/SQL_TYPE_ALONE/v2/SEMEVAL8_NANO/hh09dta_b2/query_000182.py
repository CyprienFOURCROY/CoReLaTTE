def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_vlh = tables["ii_vlh"]
    
    # Merge household info with incident data on 'folio'
    merged_inr = pd.merge(df_inr, df_portad[['folio', 'ent']], on='folio', how='inner')
    merged_vlh = pd.merge(df_vlh, df_portad[['folio', 'ent']], on='folio', how='inner')
    
    # Filter households with at least one robbery incident since 2005
    # Robbery indicators: vlh12a_a, vlh12a_b, vlh12a_c
    # Values: 1 or 2 indicate rob since 2005, 3 indicates no
    # Create a boolean mask for households with any rob since 2005
    rob_mask = (
        (merged_vlh['vlh12a_a'] == 1) | 
        (merged_vlh['vlh12a_b'] == 2)
    )
    households_with_robbery_since_2005 = merged_vlh.loc[rob_mask, 'folio'].unique()
    
    # Filter households that have experienced at least one robbery since 2005
    households_rob_since_2005 = merged_vlh[merged_vlh['folio'].isin(households_with_robbery_since_2005)]
    
    # For these households, get total robberies since 2005
    # 'vlh18a' is total times entered rob house/business/parcel since 2005
    rob_counts = households_rob_since_2005.groupby('folio')['vlh18a'].max().reset_index()
    rob_counts.columns = ['folio', 'total_robberies_since_2005']
    
    # Compute overall average of total robberies among households that experienced at least one incident
    overall_avg = rob_counts['total_robberies_since_2005'].mean()
    
    # Filter households with total robberies above the overall average
    above_avg = rob_counts[rob_counts['total_robberies_since_2005'] > overall_avg]
    
    # Count number of such households per state
    # Merge with portad to get 'ent' (state)
    result = pd.merge(above_avg, df_portad[['folio', 'ent']], on='folio', how='left')
    
    # Count households per state
    state_counts = result['ent'].value_counts()
    
    # Get top 5 states with most households above the average
    top_states = state_counts.head(5)
    
    # Map 'ent' codes to state names (from description)
    ent_map = {
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
    
    # Prepare final DataFrame
    final_df = pd.DataFrame({
        'state_code': top_states.index,
        'households_above_avg': top_states.values
    })
    final_df['state_name'] = final_df['state_code'].map(ent_map)
    
    # Return only top 5 states with their counts
    return final_df[['state_name', 'households_above_avg']]