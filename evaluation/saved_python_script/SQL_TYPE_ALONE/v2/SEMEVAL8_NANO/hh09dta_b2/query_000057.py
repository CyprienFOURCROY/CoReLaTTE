def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]
    df_su = tables["ii_su"]
    df_se = tables["ii_se"]
    df_su_enriched = tables["ii_su_enriched"]
    df_ah_enriched = tables["ii_ah_enriched"]
    df_se_enriched = tables["ii_se_enriched"]
    
    # Merge portad with inr on 'folio'
    port_inr = pd.merge(df_portad, df_inr, on='folio', how='inner')
    
    # Filter households that use land for farming
    land_farming = port_inr[df_inr['su01'] == 1]
    
    # Merge with 'ii_ah' to get motor vehicle ownership
    land_farming_ah = pd.merge(land_farming, df_ah, on=['folio', 'ls'], how='inner')
    
    # Filter households that own a motor vehicle ('ah03d' == 1)
    households_with_vehicle = land_farming_ah[land_farming_ah['ah03d'] == 1]
    
    # Merge with 'ii_se' to get seed expenses ('se02ea_1' indicates knowledge, but seed expense is in 'se02ea_2')
    seed_data = pd.merge(households_with_vehicle, df_se, on=['folio', 'ls'], how='inner')
    
    # Filter households with positive seed expenses ('se02ea_2' > 0)
    seed_positive = seed_data[seed_data['se02ea_2'] > 0]
    
    # Calculate overall average seed expense among all households with positive seed expenses
    overall_avg_seed = seed_positive['se02ea_2'].mean()
    
    # Filter households with seed expenses below the overall average
    below_avg_seed = seed_positive[seed_positive['se02ea_2'] < overall_avg_seed]
    
    # Select Household IDs and seed expenses
    result = below_avg_seed[['folio', 'se02ea_2']]
    
    # Rename columns for clarity
    result = result.rename(columns={'se02ea_2': 'seed_expense'})
    
    return result