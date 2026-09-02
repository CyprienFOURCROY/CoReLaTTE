def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    nna = tables["ii_nna"]
    
    # Filter households with at least one member younger than 30
    households_under_30 = portad[portad['edad'] < 30]['folio'].unique()
    
    # Filter households that own or share a non-agricultural business
    nna_households = nna[nna['nna01'] == 1]['folio'].unique()
    
    # Filter households with zero robberies/break-ins since 2005
    # For this, check 'vlh12a', 'vlh12a_a', 'vlh12a_b', 'vlh12a_c' columns
    # 'vlh12a' indicates if entered force rob into current house
    # 'vlh12a_a' and 'vlh12a_b' indicate if entered force rob since 2005
    # 'vlh12a_c' indicates no entry since 2005
    # We consider households with no entries in these columns or marked as no rob since 2005
    rob_columns = ['vlh12a', 'vlh12a_a', 'vlh12a_b', 'vlh12a_c']
    # Merge relevant columns into a single DataFrame
    # First, filter households that have data in 'vlh12a' or 'vlh12a_a'/'vlh12a_b'/'vlh12a_c'
    # For simplicity, consider households where all rob columns are either NaN or indicate no rob since 2005
    # Create a DataFrame with relevant columns
    rob_df = tables["ii_vlh"][['folio'] + rob_columns]
    # Fill NaNs with a default value indicating no rob
    rob_df_filled = rob_df.fillna({'vlh12a': 3, 'vlh12a_a': 3, 'vlh12a_b': 3, 'vlh12a_c': 3})
    # Households with no rob since 2005: 'vlh12a_c' == 1 or 'vlh12a_a' == 2 or 'vlh12a_b' == 2
    # But since 'vlh12a_c' == 3 indicates no entry since 2005, and 'vlh12a_a'/'b' == 2 indicates rob since 2005
    # We want households with no rob since 2005: 'vlh12a_c' == 3 and 'vlh12a_a' != 2 and 'vlh12a_b' != 2
    no_rob_mask = (
        (rob_df_filled['vlh12a_c'] == 3) &
        (rob_df_filled['vlh12a_a'] != 2) &
        (rob_df_filled['vlh12a_b'] != 2)
    )
    households_no_rob_since_2005 = rob_df[no_rob_mask]['folio'].unique()
    
    # Find households that satisfy all conditions
    valid_households = set(households_under_30) & set(nna_households) & set(households_no_rob_since_2005)
    
    # Now, get the households' data with their state
    result = portad[portad['folio'].isin(valid_households)]
    
    # Group by 'ent' (state), count households
    grouped = result.groupby('ent').size().reset_index(name='household_count')
    
    # Map 'ent' codes to state names for clarity (optional)
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
    grouped['state'] = grouped['ent'].map(state_map)
    # Order from highest to lowest
    result_df = grouped[['state', 'household_count']].sort_values(by='household_count', ascending=False).reset_index(drop=True)
    return result_df