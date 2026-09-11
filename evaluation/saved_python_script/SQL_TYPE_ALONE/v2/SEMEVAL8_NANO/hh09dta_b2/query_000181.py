def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    ah = tables["ii_ah"]
    
    # Filter households with at least one adult (age >= 18)
    adults = portad[portad['edad'] >= 18]
    households_with_adult = adults['folio'].unique()
    
    # Filter households that have at least one adult
    portad_adult = portad[portad['folio'].isin(households_with_adult)]
    
    # Count number of adults per household
    adult_counts = portad_adult.groupby('folio').size().reset_index(name='adult_count')
    
    # Keep only households with at least one adult
    households_with_adult = adult_counts[adult_counts['adult_count'] >= 1]['folio']
    
    # Filter portad to households with at least one adult
    portad_filtered = portad[portad['folio'].isin(households_with_adult)]
    
    # Merge with ah to get individual info
    ah_filtered = ah[ah['folio'].isin(households_with_adult)]
    
    # Merge portad and ah on folio and ls
    merged = pd.merge(ah_filtered, portad_filtered[['folio', 'edad']], on='folio', how='inner')
    
    # Filter for adults only (age >= 18)
    adults_only = merged[merged['edad'] >= 18]
    
    # For each household, check if any adult owns an electronic device (ah04e_1 == 1)
    # Create a boolean indicator per household
    electronic_ownership = (
        adults_only.groupby('folio')['ah04e_1']
        .apply(lambda x: 1 if (x == 1).any() else 0)
        .reset_index()
    )
    
    # Merge with households to get state info
    households_info = portad[['folio', 'ent']].drop_duplicates()
    households_electronic = pd.merge(households_info, electronic_ownership, on='folio', how='left')
    households_electronic['ah04e_1'] = households_electronic['ah04e_1'].fillna(0).astype(int)
    
    # Count households owning electronic devices per state
    result = (
        households_electronic.groupby('ent')['ah04e_1']
        .sum()
        .reset_index()
        .rename(columns={'ent': 'state', 'ah04e_1': 'households_with_electronic'})
    )
    
    # Filter states with at least 50 households that include an adult
    # First, count total households with adults per state
    households_with_adult_df = portad[portad['folio'].isin(households_with_adult)]
    total_households_state = (
        households_with_adult_df[['folio', 'ent']]
        .drop_duplicates()
        .groupby('ent')
        .size()
        .reset_index(name='total_households')
    )
    
    # Merge to filter states with at least 50 households
    merged_counts = pd.merge(result, total_households_state, on='ent', how='left')
    filtered = merged_counts[merged_counts['total_households'] >= 50]
    
    # Rank from highest to lowest
    filtered_sorted = filtered.sort_values(by='households_with_electronic', ascending=False)
    
    # Map state codes to labels (optional, not required, but for clarity)
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
    filtered_sorted['state_name'] = filtered_sorted['state'].map(state_mapping)
    
    # Select final columns
    final_df = filtered_sorted[['state_name', 'households_with_electronic']]
    final_df = final_df.rename(columns={'state_name': 'State', 'households_with_electronic': 'Households with Electronic Device'})
    
    return final_df.reset_index(drop=True)