def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    ah = tables["ii_ah"]
    nna = tables["ii_nna"]
    
    # Merge portad with se on 'folio'
    merged = pd.merge(portad, se, on='folio', how='inner')
    
    # Filter households with at least one adult (edad >= 18)
    adults = merged[merged['edad'] >= 18]
    households_with_adults = adults['folio'].unique()
    
    # Filter households with positive electronic device value (ah04e_1 > 0 or ah04e_2 > 0)
    # Note: Values can be NaN, so check for > 0 after filling NaNs with 0
    ah_filtered = ah.copy()
    ah_filtered['ah04e_1'] = ah_filtered['ah04e_1'].fillna(0)
    ah_filtered['ah04e_2'] = ah_filtered['ah04e_2'].fillna(0)
    ah_pos_devices = ah_filtered[(ah_filtered['ah04e_1'] > 0) | (ah_filtered['ah04e_2'] > 0)]
    households_with_devices = ah_pos_devices['folio'].unique()
    
    # Find households with at least one adult and positive electronic devices
    households_of_interest = set(households_with_adults).intersection(set(households_with_devices))
    
    # For these households, compute max electronic device value per household
    ah_interest = ah[ah['folio'].isin(households_of_interest)].copy()
    # Fill NaNs with 0 for comparison
    ah_interest['ah04e_1'] = ah_interest['ah04e_1'].fillna(0)
    ah_interest['ah04e_2'] = ah_interest['ah04e_2'].fillna(0)
    # Compute maximum per individual
    ah_interest['max_elec'] = ah_interest[['ah04e_1', 'ah04e_2']].max(axis=1)
    # Aggregate to household level: maximum reported electronic device value per household
    household_max = ah_interest.groupby('folio')['max_elec'].max()
    
    # Calculate overall mean of these maximums
    overall_mean = household_max.mean()
    
    # Identify households with at least one death in last five years
    households_with_death = se[se['se01a'] == 1]['folio'].unique()
    
    # For households with death, get their max electronic device value
    household_max_death = household_max[household_max.index.isin(households_with_death)]
    # Compute mean among households with death
    mean_death = household_max_death.mean()
    
    # Prepare result
    result_value = mean_death if pd.notnull(mean_death) else None
    
    return pd.DataFrame(
        {"comparison": [result_value, overall_mean, result_value > overall_mean]}
    )