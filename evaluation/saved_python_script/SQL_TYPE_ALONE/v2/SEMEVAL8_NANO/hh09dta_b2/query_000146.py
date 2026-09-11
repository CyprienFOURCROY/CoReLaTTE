def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    ah = tables["ii_ah"]
    
    # Filter households where at least one member owns a motor vehicle
    motor_vehicle_mask = ah['ah03d'] == 1
    households_with_vehicle = ah[motor_vehicle_mask]['folio'].unique()
    
    # Filter portad for these households
    portad_filtered = portad[portad['folio'].isin(households_with_vehicle)]
    
    # Merge portad with ah to get 'ls' (individual ID) for households with motor vehicle
    ah_filtered = ah[ah['folio'].isin(portad_filtered['folio'])]
    
    # Merge to get 'ls' for individuals in these households
    merged_ah = pd.merge(ah_filtered[['folio', 'ls']], portad_filtered[['folio']], on='folio', how='inner')
    
    # Merge with ii_ah to get 'ah03d' and 'ls'
    df_ah = pd.merge(merged_ah, tables["ii_ah"], on=['folio', 'ls'], how='left')
    
    # Filter individuals who own a motor vehicle
    owns_motor_vehicle = df_ah['ah03d'] == 1
    
    # Get households where at least one member owns a motor vehicle
    households_motor_vehicle = df_ah[owns_motor_vehicle]['folio'].unique()
    
    # Filter portad for these households
    portad_mv = portad[portad['folio'].isin(households_motor_vehicle)]
    
    # Filter households with at least 30 members
    household_counts = portad_mv.groupby('folio').size()
    households_30plus = household_counts[household_counts >= 30].index
    
    # Filter portad for these households
    portad_final = portad[portad['folio'].isin(households_30plus)]
    
    # Merge with ii_vlh to get 'vlh01x' (Feel safe at home?)
    df_vlh = pd.merge(portad_final[['folio']], tables["ii_vlh"], on='folio', how='left')
    
    # Calculate overall average 'vlh01x' for households with at least one member owning a motor vehicle
    households_with_mv = set(households_with_vehicle)
    relevant_households = df_vlh[df_vlh['folio'].isin(households_with_mv)]
    overall_avg = relevant_households['vlh01x'].mean()
    
    # For each household, compute average 'vlh01x'
    household_avg = relevant_households.groupby('folio')['vlh01x'].mean().reset_index()
    
    # Get households with at least 30 members
    household_sizes = portad[portad['folio'].isin(households_with_mv)].groupby('folio').size()
    large_households = household_sizes[household_sizes >= 30].index
    
    # Filter household averages for these households
    large_households_avg = household_avg[household_avg['folio'].isin(large_households)]
    
    # Get the average 'vlh01x' for these households
    large_households_avg = large_households_avg.rename(columns={'vlh01x': 'avg_vlh01x'})
    
    # Merge with portad to get 'ent' (state)
    household_states = portad[['folio', 'ent']].drop_duplicates()
    merged = pd.merge(large_households_avg, household_states, on='folio', how='left')
    
    # Filter households with average 'vlh01x' higher than overall average
    filtered = merged[merged['avg_vlh01x'] > overall_avg]
    
    # Count households per state
    state_counts = filtered.groupby('ent').size()
    # Filter states with at least 30 households
    states_30plus = state_counts[state_counts >= 30].index
    
    # Filter for these states
    final_df = filtered[filtered['ent'].isin(states_30plus)]
    
    # Map 'ent' codes to state names (from metadata)
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
    final_df['state'] = final_df['ent'].map(ent_map)
    
    # Select and order columns
    result = final_df[['state', 'avg_vlh01x', 'folio']]
    result = result.rename(columns={'avg_vlh01x': 'Average Feel Safe at Home'})
    result = result.sort_values(by='Average Feel Safe at Home', ascending=False).reset_index(drop=True)
    
    return result