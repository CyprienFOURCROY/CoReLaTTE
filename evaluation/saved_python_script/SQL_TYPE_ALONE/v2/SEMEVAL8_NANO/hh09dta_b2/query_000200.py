def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_inr = tables["ii_inr"]
    
    # Filter households that reported receiving income from '70 y más' in last 12 months
    # 'in01a11_1' indicates participation in '70 y más' program
    households_70_plus_income = df_in[df_in['in01a11_1'] == 1]['folio'].unique()
    
    # Filter households that include at least one resident aged 70 or older
    # 'edad' column: age of individual
    # Merge portad with in order to identify residents aged 70+ per household
    portad_70plus = df_portad[df_portad['edad'] >= 70]
    households_with_70plus_residents = portad_70plus['folio'].unique()
    
    # Find households that satisfy both conditions
    households_both = set(households_70_plus_income).intersection(set(households_with_70plus_residents))
    
    # Filter in table for these households
    df_both = df_in[df_in['folio'].isin(households_both)]
    
    # Count households per state that meet both conditions
    # Merge with portad to get 'ent' (state) info
    df_both_merged = df_both.merge(df_portad[['folio', 'ent']], on='folio', how='left')
    
    # Group by 'ent' and count unique households
    result = df_both_merged.groupby('ent')['folio'].nunique().reset_index()
    result.columns = ['ent', 'household_count']
    
    # Calculate the overall average number of households across all states
    overall_avg = result['household_count'].mean()
    
    # Filter states with at least the average
    states_above_avg = result[result['household_count'] >= overall_avg]
    
    # Map 'ent' codes to state names for clarity
    ent_mapping = {
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
    states_above_avg['state'] = states_above_avg['ent'].map(ent_mapping)
    
    # Select only relevant columns
    result_final = states_above_avg[['state', 'household_count']]
    
    return result_final