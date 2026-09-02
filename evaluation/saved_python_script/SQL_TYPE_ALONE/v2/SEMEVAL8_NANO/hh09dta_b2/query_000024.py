def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]
    
    # Filter households that participated and received income from an Other Government Program in last 12 months
    # 'in01a10_1' indicates participation and receipt (value=1)
    households_in_program = df_in[
        (df_in['in01a10_1'] == 1)
    ]['folio'].unique()
    
    # Filter individuals aged 30-50 with Individual ID 01 or 02
    # 'ls' is individual ID, 'edad' is age
    individuals_filtered = df_portad[
        (df_portad['folio'].isin(households_in_program)) &
        (df_portad['edad'].between(30, 50)) &
        (df_portad['ls'].isin([1, 2]))
    ]
    
    # Get the relevant household folios after filtering individuals
    filtered_folios = individuals_filtered['folio'].unique()
    
    # Filter households that meet the individual criteria
    households_filtered = df_in[
        (df_in['folio'].isin(filtered_folios))
    ]
    
    # Merge with household info to get 'ent' (state)
    households_with_state = households_filtered.merge(
        df_portad[['folio', 'ent']],
        on='folio',
        how='left'
    ).drop_duplicates(subset='folio')
    
    # Filter households that participated and received income from 'in01a10_1' == 1
    households_in_program_df = households_with_state[
        households_with_state['folio'].isin(households_in_program)
    ]
    
    # Merge with household ownership data to get 'ah04f_2' (washing machine/stove value)
    household_assets = households_in_program_df.merge(
        df_ah[['folio', 'ah04f_2']],
        on='folio',
        how='left'
    )
    
    # Drop households with missing 'ah04f_2' (if any)
    household_assets = household_assets.dropna(subset=['ah04f_2'])
    
    # Calculate overall mean of 'ah04f_2'
    overall_mean = household_assets['ah04f_2'].mean()
    
    # Calculate mean per state
    state_means = household_assets.groupby('ent')['ah04f_2'].mean().reset_index()
    
    # Filter states with mean above overall mean
    states_above_mean = state_means[state_means['ah04f_2'] > overall_mean]
    
    # Map state codes to state names (optional, only if needed for clarity)
    # But since only state codes are provided, we keep codes
    # Sort by mean descending
    states_above_mean_sorted = states_above_mean.sort_values(by='ah04f_2', ascending=False).reset_index(drop=True)
    
    # Return DataFrame with state code and their averages
    return states_above_mean_sorted[['ent', 'ah04f_2']]