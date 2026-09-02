def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_vlh = tables["ii_vlh"]
    
    # Step 1: Filter households with at least 30 households that did NOT produce/sell any listed goods in last 12 months
    # and know a family/friend robbed in last 5 years.
    # Conditions:
    # - For production/sell: all inr02a to inr02k == 3 (No)
    # - For knowing robbed in last 5 years: vlh10a == 1 (Yes)
    # - Group by 'folio' to count households per household
    inr_cols = ['inr02a','inr02b','inr02c','inr02d','inr02e','inr02f','inr02g','inr02h','inr02i','inr02j','inr02k']
    households_inr = df_inr[['folio'] + inr_cols].dropna()
    households_inr['all_no'] = households_inr[inr_cols].eq(3).all(axis=1)
    households_inr_no_goods = households_inr[households_inr['all_no']]
    
    # Merge with vlh to filter households that know a robbery in last 5 years
    households_vlh = df_vlh[['folio','vlh10a']]
    merged = pd.merge(households_inr_no_goods[['folio']], households_vlh, on='folio', how='inner')
    # Filter households where vlh10a == 1 (Yes)
    households_robbed_recent = merged[merged['vlh10a'] == 1]
    
    # Count households per household (folio)
    household_counts = households_robbed_recent['folio'].value_counts()
    # Filter households with at least 30 households
    eligible_folios = household_counts[household_counts >= 30].index.tolist()
    
    # Step 2: For these households, determine their state and whether they feel unsafe or very unsafe at home
    # Merge with portad to get 'ent' (state)
    eligible_df = df_portad[df_portad['folio'].isin(eligible_folios)]
    # Filter for 'vlh04' (feel safe at home): 1 (Very safe), 2 (Safe), 3 (Unsafe), 4 (Very unsafe)
    # We are interested in 'unsafe' or 'very unsafe' -> vlh04 in [3,4]
    unsafe_mask = eligible_df['vlh04'].isin([3,4])
    unsafe_df = eligible_df[unsafe_mask]
    
    # Group by 'ent' (state) and compute total eligible households and those feeling unsafe
    total_counts = eligible_df.groupby('ent')['folio'].nunique()
    unsafe_counts = unsafe_df.groupby('ent')['folio'].nunique()
    
    # Compute average number of households per state
    avg_households = total_counts.mean()
    
    # Filter states with total households >= 30 and above average number feeling unsafe
    qualifying_states = total_counts[(total_counts >= 30) & (total_counts > avg_households)].index
    
    # Prepare final DataFrame
    result = pd.DataFrame({
        'state': qualifying_states,
        'total_households': total_counts.loc[qualifying_states],
        'unsafe_households': unsafe_counts.reindex(qualifying_states).fillna(0).astype(int)
    })
    
    # Sort by number of unsafe households descending
    result = result.sort_values(by='unsafe_households', ascending=False).reset_index(drop=True)
    
    return result[['state', 'total_households', 'unsafe_households']]