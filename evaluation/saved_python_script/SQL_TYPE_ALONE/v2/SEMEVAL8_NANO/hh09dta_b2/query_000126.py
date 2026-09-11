def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]
    
    # Merge inr and portad on 'folio'
    inr_portad = pd.merge(df_inr, df_portad, on='folio', how='inner')
    # Merge with su on 'folio'
    inr_portad_su = pd.merge(inr_portad, df_su, on='folio', how='inner')
    
    # Filter households that use a plot/land for farming
    households_with_land = inr_portad_su[inr_portad_su['su01'] == 1]
    
    # Filter households that produced/sold both meat and eggs in last 12 months
    # 'inr02c' = meat, 'inr02d' = eggs
    # Values: 1=Yes, 3=No
    produce_meat_eggs = households_with_land[
        (households_with_land['inr02c'] == 1) & (households_with_land['inr02d'] == 1)
    ]
    
    # Group by household ('folio') to get list of individuals per household
    household_groups = produce_meat_eggs.groupby('folio')
    
    # Filter households with at least 30 individuals
    households_with_size = household_groups.filter(lambda g: len(g) >= 30)
    
    # Merge back with portad to get 'edad' and 'ent' for individuals
    merged = pd.merge(households_with_size, df_portad, on='folio', how='left')
    
    # Calculate overall average age among these individuals
    overall_avg_age = merged['edad'].mean()
    
    # For each state, compute average age and count
    state_stats = (
        merged.groupby('ent')
        .agg(
            average_age=('edad', 'mean'),
            count_individuals=('edad', 'size')
        )
        .reset_index()
    )
    
    # Filter states with at least 30 individuals
    states_filtered = state_stats[state_stats['count_individuals'] >= 30]
    
    # Select states with average age higher than overall average
    result = states_filtered[states_filtered['average_age'] > overall_avg_age]
    
    # Sort from highest to lowest average age
    result_sorted = result.sort_values(by='average_age', ascending=False)
    
    # Return only 'ent', 'average_age', 'count_individuals'
    return result_sorted[['ent', 'average_age', 'count_individuals']]