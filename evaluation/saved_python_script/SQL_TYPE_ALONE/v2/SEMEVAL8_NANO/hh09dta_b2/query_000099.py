def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_se = tables["ii_se"]
    df_inr = tables["ii_inr"]
    df_in_enriched = tables["ii_in_enriched"]
    df_se_enriched = tables["ii_se_enriched"]
    
    # Filter households where:
    # - produce/sell fattening animals (inr02j == 1)
    # - received income from Other Government Program (in01a10_1 == 1)
    # Merge relevant tables on 'folio'
    merged_inr = pd.merge(df_inr, df_in_enriched[['folio', 'in01a10_1']], on='folio', how='inner')
    merged_in = pd.merge(df_in, merged_inr[['folio', 'in01a10_1']], on='folio', how='inner')
    merged_se = pd.merge(df_se, df_se_enriched[['folio']], on='folio', how='inner')
    merged_portad = pd.merge(df_portad, merged_in[['folio']], on='folio', how='inner')
    
    # Filter households with produce/sell fattening animals and income from other gov program
    condition = (
        (merged_inr['inr02j'] == 1) &
        (merged_in['in01a10_1'] == 1)
    )
    households_filtered = merged_in[condition]['folio'].unique()
    
    # Filter individuals aged 18+ in these households
    individuals = merged_portad[merged_portad['folio'].isin(households_filtered)]
    adults = individuals[individuals['edad'] >= 18]
    
    # Count number of adults per household
    adults_count = adults.groupby('ent').size().reset_index(name='adult_count')
    
    # Calculate overall average
    overall_avg = adults_count['adult_count'].mean()
    
    # Get states with above-average number of such adults
    above_avg_states = adults_count[adults_count['adult_count'] > overall_avg]
    
    # Merge with portad to get state info
    result = pd.merge(above_avg_states, df_portad[['folio', 'ent']], on='folio', how='left')
    
    # Count adults per state
    state_counts = result.groupby('ent')['adult_count'].sum().reset_index()
    
    # Map 'ent' codes to state names
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
    state_counts['state'] = state_counts['ent'].map(state_map)
    # Order from highest to lowest
    state_counts = state_counts.sort_values(by='adult_count', ascending=False).reset_index(drop=True)
    # Select only 'state' and 'adult_count'
    result_df = state_counts[['state', 'adult_count']]
    return result_df