def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    su = tables["ii_su"]
    
    # Filter households with at least one adult (assuming 'edad' > 0)
    # and 'ent' (state) is not null
    households_with_adults = portad[portad['edad'] > 0].dropna(subset=['ent'])
    household_ids_with_adults = households_with_adults['folio'].unique()

    # Filter crh for households with adults
    crh_filtered = crh[crh['folio'].isin(household_ids_with_adults)]
    
    # Filter households that have land for farming ('su01' == 1)
    su_land = su[(su['folio'].isin(household_ids_with_adults)) & (su['su01'] == 1)]
    land_households = su_land['folio'].unique()

    # Filter crh for households with land for farming
    crh_land = crh[crh['folio'].isin(land_households)]
    
    # Filter crh for households that reported owing money in last 12 months ('crh02_1' == 1)
    crh_debt = crh_land[crh_land['crh02_1'] == 1]
    
    # Count households with land and debt per household
    households_with_land_and_debt = crh_debt.groupby('folio').size().reset_index(name='count')
    # Merge with households with adults to ensure only households with adults
    households_with_land_and_debt = households_with_land_and_debt[
        households_with_land_and_debt['folio'].isin(household_ids_with_adults)
    ]
    
    # Get list of households with land, debt, and adults
    households_with_land_and_debt_list = households_with_land_and_debt['folio'].unique()
    
    # Calculate average number of such households per state
    # First, get the households with land, debt, and adults with their states
    households_info = portad[portad['folio'].isin(households_with_land_and_debt_list)][['folio', 'ent']]
    # Count total households with adults per state
    total_households_per_state = portad[portad['folio'].isin(household_ids_with_adults)].groupby('ent').size().reset_index(name='total_adult_households')
    # Count households with land, debt, and adults per state
    households_with_land_debt_info = households_info.merge(households_with_land_and_debt, on='folio')
    count_per_state = households_with_land_debt_info.groupby('ent').size().reset_index(name='land_debt_households')
    # Merge to compute ratio
    ratio_df = count_per_state.merge(total_households_per_state, on='ent')
    ratio_df['ratio'] = ratio_df['land_debt_households'] / ratio_df['total_adult_households']
    average_ratio = ratio_df['ratio'].mean()

    # Select states with ratio > average_ratio
    states_above_avg = ratio_df[ratio_df['ratio'] > average_ratio]

    # For each such state, count households with land, debt, and adults
    result = states_above_avg[['ent', 'land_debt_households']].rename(columns={'ent': 'state', 'land_debt_households': 'households_count'})

    # Rank from highest to lowest
    result = result.sort_values(by='households_count', ascending=False).reset_index(drop=True)

    return result