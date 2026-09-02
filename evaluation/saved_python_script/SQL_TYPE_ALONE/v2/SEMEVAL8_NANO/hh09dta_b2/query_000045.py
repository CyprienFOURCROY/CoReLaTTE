def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]
    
    # Filter households with at least one member aged 60 or older
    households_with_elderly = df_portad[df_portad['edad'] >= 60]['folio'].unique()
    
    # Filter households that reported a death in the last five years (se01a == 1)
    households_with_death = df_se[df_se['se01a'] == 1]['folio'].unique()
    
    # Merge to get households satisfying both conditions
    households_filtered = set(households_with_elderly) & set(households_with_death)
    
    # Create a DataFrame of these households
    df_households = pd.DataFrame({'folio': list(households_filtered)})
    
    # Calculate overall household average value of wash machine/stove assets
    # First, filter for households in the filtered set
    df_ah_filtered = df_ah[df_ah['folio'].isin(households_filtered)]
    
    # Compute total value of wash machine/stove assets per household
    # Values are in columns 'ah04f_1' and 'ah04f_2'
    df_ah_filtered['wash_value'] = df_ah_filtered[['ah04f_1', 'ah04f_2']].max(axis=1)
    
    # Compute overall average
    overall_avg = df_ah_filtered['wash_value'].mean()
    
    # Filter households with total wash asset value above the overall average
    households_above_avg = df_ah_filtered[df_ah_filtered['wash_value'] > overall_avg]['folio']
    
    # Final set of households satisfying all conditions
    final_households = set(households_with_elderly) & set(households_with_death) & set(households_above_avg)
    
    # Return the count as a DataFrame
    return pd.DataFrame({"count": [len(final_households)]})