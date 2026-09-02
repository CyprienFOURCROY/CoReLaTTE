def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_vlh = tables["ii_vlh"]
    
    # Merge portad and inr on 'folio'
    merged = pd.merge(df_portad, df_inr, on='folio', how='inner')
    
    # Filter households with at least 100 surveyed households per state
    household_counts = merged.groupby('ent').size()
    states_with_100_plus = household_counts[household_counts >= 100].index
    
    # Filter merged data to only include these states
    filtered = merged[merged['ent'].isin(states_with_100_plus)]
    
    # For each household, determine if they know a family or friend robbed house/business in last 12 months
    # Conditions: 'vlh10a' == 1 (Yes)
    # Merge with vlh to get 'vlh10a' info
    df_vlh_relevant = df_vlh[['folio', 'vlh10a']]
    household_vlh = pd.merge(filtered[['folio', 'ent']], df_vlh_relevant, on='folio', how='left')
    
    # Create indicator for knowing a family/friend robbed house/business in last 12 months
    household_vlh['knows_robbed_last12m'] = household_vlh['vlh10a'].fillna(3) == 1
    
    # Count households per state
    total_households_per_state = household_vlh.groupby('ent').size()
    # Count households that know someone robbed in last 12 months
    robbed_household_counts = household_vlh.groupby('ent')['knows_robbed_last12m'].sum()
    
    # Prepare result DataFrame
    result = pd.DataFrame({
        'state_code': total_households_per_state.index,
        'total_households': total_households_per_state.values,
        'know_robbed_last12m': robbed_household_counts.values
    })
    
    # Rank states from highest to lowest on 'know_robbed_last12m'
    result = result.sort_values(by='know_robbed_last12m', ascending=False).reset_index(drop=True)
    
    # Map 'ent' codes to state names if needed (optional, not specified)
    # For now, return state codes
    return result[['state_code', 'total_households', 'know_robbed_last12m']]