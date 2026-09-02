def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    
    # Merge portad with crh on 'folio'
    merged = pd.merge(df_portad, df_crh, on='folio', how='inner')
    
    # Filter for households with 'crh12a' indicating forced robbery since 2005
    # 'crh12a' codes:
    # 1: Yes, into current dwelling
    # 2: Yes, into another dwelling
    # 3: No
    # We want households with 'crh12a' == 1 or 2
    robbed_households = merged[merged['crh12a'].isin([1, 2])]
    
    # Count number of incidents per household
    incidents_per_household = robbed_households.groupby('folio').size().reset_index(name='incident_count')
    
    # Merge back with portad to get 'ent' (state)
    incidents_with_state = pd.merge(incidents_per_household, df_portad[['folio', 'ent']], on='folio', how='left')
    
    # Count households per state with at least one incident
    households_per_state = incidents_with_state.groupby('ent')['folio'].nunique().reset_index(name='household_count')
    
    # Filter states with at least 100 households that experienced incidents
    states_with_100_households = households_per_state[households_per_state['household_count'] >= 100]
    
    # For these states, compute total incidents
    total_incidents_per_state = incidents_with_state.groupby('ent')['incident_count'].sum().reset_index()
    
    # Calculate average number of incidents across all states with any incidents
    avg_incidents = total_incidents_per_state['incident_count'].mean()
    
    # Filter states where total incidents exceed the average
    states_above_avg = total_incidents_per_state[total_incidents_per_state['incident_count'] > avg_incidents]
    
    # Rank states by total incidents descending
    ranked_states = states_above_avg.sort_values(by='incident_count', ascending=False)
    
    # Map 'ent' codes to state names (optional, but not required for output)
    # For output, just return 'ent' and 'incident_count'
    result = ranked_states[['ent', 'incident_count']].reset_index(drop=True)
    
    return result