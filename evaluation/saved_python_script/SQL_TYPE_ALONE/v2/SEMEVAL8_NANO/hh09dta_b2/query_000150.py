def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    crh = tables["ii_crh"]
    
    # Merge portad with crh on 'folio' to get respondent info with household info
    portad_crh = pd.merge(portad, crh, on='folio', how='inner')
    
    # Filter households where respondent feels unsafe or very unsafe at home
    # 'vlh04' indicates feeling safe at home:
    # 3: Unsafe, 4: Very unsafe
    unsafe_mask = portad_crh['vlh04'].isin([3, 4])
    unsafe_households = portad_crh[unsafe_mask]
    
    # Filter households with reported debt values (crh02_2 is the debt amount in pesos)
    debt_mask = portad_crh['crh02_2'].notna()
    households_with_debt = portad_crh[debt_mask]
    
    # Calculate national average total debt among households with reported debt
    # 'crh04b' indicates debt amount in pesos, but 'crh04_2' is the total debts + interests
    # Use 'crh04_2' for total debt
    total_debt_series = households_with_debt['crh04_2']
    national_avg_debt = total_debt_series.mean()
    
    # For each household, get 'edad' and 'crh04_2'
    # Merge with portad to get 'edad'
    households_debt_age = pd.merge(households_with_debt[['folio', 'edad', 'crh04_2']], portad[['folio', 'ent']], on='folio', how='inner')
    
    # For each state, compute average total debt, average age, and count of households
    state_stats = (
        households_debt_age
        .groupby('ent')
        .agg(
            avg_total_debt=('crh04_2', 'mean'),
            avg_age=('edad', 'mean'),
            household_count=('folio', 'count')
        )
        .reset_index()
    )
    
    # Filter states where average total debt exceeds the national average
    high_debt_states = state_stats[state_stats['avg_total_debt'] > national_avg_debt]
    
    # Order from highest to lowest average debt
    result = high_debt_states.sort_values(by='avg_total_debt', ascending=False)
    
    # Map 'ent' codes to state names for clarity
    state_mapping = {
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
    result['state_name'] = result['ent'].map(state_mapping)
    
    # Select relevant columns
    final_df = result[['state_name', 'avg_total_debt', 'avg_age', 'household_count']]
    
    return final_df