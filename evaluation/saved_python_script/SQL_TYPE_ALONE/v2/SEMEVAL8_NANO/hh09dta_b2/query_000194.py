def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    se = tables["ii_se"]
    
    # Filter portad for age between 18 and 24
    age_mask = portad['edad'].between(18, 24, inclusive='both')
    portad_18_24 = portad[age_mask]
    
    # Merge portad with ah on 'folio' and 'ls'
    merged_ah = pd.merge(portad_18_24, ah, on=['folio', 'ls'], how='left')
    
    # Filter households that own at least one electronic device (ah03e == 1)
    device_mask = merged_ah['ah03e'] == 1
    households_with_device = merged_ah[device_mask]
    
    # Group by household to get total individuals and individuals aged 18-24 with device
    household_counts = households_with_device.groupby('folio').agg(
        total_individuals=('folio', 'count'),
        age_18_24_with_device=('folio', 'size')
    ).reset_index()
    
    # Calculate the overall average of age_18_24_with_device across all households
    overall_avg = household_counts['age_18_24_with_device'].mean()
    
    # Identify households with more than the average
    households_above_avg = household_counts[
        household_counts['age_18_24_with_device'] > overall_avg
    ]
    
    # Merge with portad to get 'ent' (state) info for these households
    # First, get unique household info from portad
    household_info = portad[['folio', 'ent']].drop_duplicates()
    result = pd.merge(households_above_avg, household_info, on='folio', how='left')
    
    # For each state, compute total 18-24-year-olds and total individuals in device-owning households
    # Filter portad for age 18-24
    portad_18_24_full = portad[age_mask]
    # Merge with households_above_avg to filter only relevant households
    relevant_households = result[['folio', 'ent']]
    portad_relevant = pd.merge(portad_18_24_full, relevant_households, on='folio', how='inner')
    
    # Group by state
    state_group = portad_relevant.groupby('ent').agg(
        count_18_24=('folio', 'count')
    ).reset_index()
    
    # For total individuals in these households (regardless of age), get total per household
    total_individuals_per_household = portad_18_24_full.groupby('folio').size().reset_index(name='total_individuals')
    # Merge with relevant households to filter only those above average
    total_in_households = pd.merge(total_individuals_per_household, relevant_households, on='folio', how='inner')
    total_in_state = total_in_households.groupby('ent').agg(
        total_in_household=('folio', 'count')
    ).reset_index()
    
    # Merge counts
    final_df = pd.merge(state_group, total_in_state, on='ent', how='left')
    # Rank by count of 18-24-year-olds
    final_df = final_df.sort_values(by='count_18_24', ascending=False).reset_index(drop=True)
    
    # Rename columns for clarity
    final_df = final_df.rename(columns={
        'ent': 'state',
        'count_18_24': 'num_18_24_years',
        'total_in_household': 'total_individuals_in_households'
    })
    
    return final_df[['state', 'num_18_24_years', 'total_individuals_in_households']]