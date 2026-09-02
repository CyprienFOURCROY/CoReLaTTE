def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    ah = tables["ii_ah"]
    ah_enriched = tables["ii_ah_enriched"]
    vlh = tables["ii_vlh"]
    vlh_enriched = tables["ii_vlh_enriched"]
    
    # Merge household info with enriched data
    # Merge portad with ah_enriched on 'folio' and 'ls'
    ah_enriched_merge = pd.merge(ah_enriched, portad[['folio', 'ent']], on='folio', how='inner')
    # Merge with vlh_enriched on 'folio'
    vlh_enriched_merge = pd.merge(vlh_enriched, portad[['folio', 'ent']], on='folio', how='inner')
    
    # Filter households that use land for farming (su01 == 1)
    land_use_mask = su['su01'] == 1
    households_with_land = su[land_use_mask][['folio']]
    
    # Filter households with at least one robbery since 2005 (vlh12a_a == 1 or vlh12a_b == 1)
    robbery_mask = (vlh_enriched['vlh12a_a'] == 1) | (vlh_enriched['vlh12a_b'] == 1)
    households_robbery = vlh_enriched[robbery_mask][['folio']]
    
    # Merge households with land and robbery
    households_land_robbery = pd.merge(households_with_land, households_robbery, on='folio', how='inner')
    
    # Get households that meet both conditions
    households_filtered = households_land_robbery['folio'].unique()
    
    # Filter ah_enriched for these households
    ah_filtered = ah_enriched_merge[ah_enriched_merge['folio'].isin(households_filtered)]
    
    # Filter vlh_enriched for these households
    vlh_filtered = vlh_enriched_merge[vlh_enriched_merge['folio'].isin(households_filtered)]
    
    # Extract 'ah04e_2' (value of electronic device) and filter for above overall mean
    ah_electronics = ah_filtered['ah04e_2']
    overall_mean = ah_electronics.mean()
    electronics_above_mean_mask = ah_electronics > overall_mean
    
    # Filter households for electronics above overall mean
    households_above_mean = ah_filtered[electronics_above_mean_mask]['folio']
    
    # Get corresponding households in vlh data
    vlh_above_mean = vlh_filtered[vlh_filtered['folio'].isin(households_above_mean)]
    
    # Merge to get 'ent' (state) info
    households_state = pd.merge(vlh_above_mean[['folio']], portad[['folio', 'ent']], on='folio', how='left')
    
    # Calculate mean electronic devices per state
    # First, get 'ent' for households with electronics above mean
    ent_series = households_state['ent']
    # Filter for households with electronics above mean
    households_electronics = ah_filtered[ah_filtered['folio'].isin(households_above_mean)]
    # Merge to get 'ent'
    households_electronics = pd.merge(households_electronics[['folio']], portad[['folio', 'ent']], on='folio', how='left')
    # Filter for above mean
    households_electronics_above_mean = households_electronics[ah_filtered['ah04e_2'].isin(ah_filtered['ah04e_2'][electronics_above_mean_mask])]
    
    # Group by 'ent' and compute mean of 'ah04e_2'
    mean_electronics_by_state = (
        pd.merge(households_electronics, portad[['folio', 'ent']], on='folio', how='left')
        .groupby('ent')['ah04e_2']
        .mean()
        .reset_index()
    )
    
    # Count households per state
    count_households = (
        households_electronics.groupby('ent')['folio']
        .nunique()
        .reset_index()
        .rename(columns={'folio': 'household_count'})
    )
    
    # Merge mean and count
    result = pd.merge(mean_electronics_by_state, count_households, on='ent')
    
    # Rank states by average electronic devices (descending)
    result = result.sort_values(by='ah04e_2', ascending=False).reset_index(drop=True)
    
    # Map 'ent' codes to state names for clarity (optional, not required)
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
    result['state'] = result['ent'].map(ent_map)
    # Select only relevant columns
    final_result = result[['state', 'ah04e_2', 'household_count']]
    return final_result