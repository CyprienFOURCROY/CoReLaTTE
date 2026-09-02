def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_su = tables["ii_su"]
    
    # Calculate overall average age
    overall_avg_age = df_portad['edad'].mean()

    # Filter households that use a plot/land for farming (su01 == 1)
    df_su_farming = df_su[df_su['su01'] == 1]
    
    # Merge with portad to get age and state info
    merged = pd.merge(df_su_farming, df_portad, on='folio', how='inner')
    
    # Filter households with at least one member aged 18-24
    households_with_18_24 = merged[merged['edad'].between(18, 24)]
    
    # For each household, compute average age
    household_avg_age = merged.groupby('folio')['edad'].mean().reset_index()
    household_avg_age.columns = ['folio', 'avg_age']
    
    # Merge back to get household info
    household_info = pd.merge(merged[['folio', 'ent']], household_avg_age, on='folio', how='left')
    
    # Filter households with average age >= overall average
    households_above_avg_age = household_info[household_info['avg_age'] >= overall_avg_age]
    
    # Count households per state that meet all criteria
    result = (
        households_above_avg_age
        .groupby('ent')
        .size()
        .reset_index(name='households_count')
    )
    
    # Get list of households that own/share non-ag business (nna01 == 1)
    nna_ownership = df_nna[df_nna['nna01'] == 1][['folio']]
    
    # Merge with households meeting criteria to find those with non-ag business owners
    households_with_non_ag = pd.merge(households_above_avg_age, nna_ownership, on='folio', how='inner')
    
    # Count households with non-ag business owners per state
    households_with_non_ag_count = (
        households_with_non_ag
        .groupby('ent')
        .size()
        .reset_index(name='households_with_non_ag')
    )
    
    # Merge counts to get final result
    final = pd.merge(result, households_with_non_ag_count, on='ent', how='left')
    
    # Fill NaN with 0 for states with no households with non-ag business owners
    final['households_with_non_ag'] = final['households_with_non_ag'].fillna(0).astype(int)
    
    # Rename 'ent' to 'state' for clarity
    final = final.rename(columns={'ent': 'state'})
    
    return final