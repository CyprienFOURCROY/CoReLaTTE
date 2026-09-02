def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]
    df_ah_enriched = tables["ii_ah_enriched"]
    df_inr_enriched = tables["ii_inr_enriched"]
    
    # Filter households with at least one member aged 18 or older
    households_with_adult = (
        df_portad[df_portad['edad'] >= 18]
        [['folio']]
        .drop_duplicates()
    )
    
    # Merge with household info to get all members of these households
    portad_adult = pd.merge(df_portad, households_with_adult, on='folio', how='inner')
    
    # Identify households with at least one member owning poultry
    poultry_owners = (
        df_ah_enriched[
            (df_ah_enriched['ah03m'] == 1)
        ][['folio']]
        .drop_duplicates()
    )
    
    # Merge to get households with poultry owners
    households_with_poultry = pd.merge(households_with_adult, poultry_owners, on='folio', how='inner')
    
    # For these households, check if any member produced or sold dairy products in last 12 months
    # Merge with inr data
    inr_households = pd.merge(df_inr, households_with_poultry, on='folio', how='inner')
    
    # Check if any member produced/sold dairy in last 12 months
    dairy_production_mask = inr_households['inr02a'] == 1
    
    # Group by household to see if any member had dairy production
    households_with_dairy = (
        inr_households[dairy_production_mask]
        [['folio']]
        .drop_duplicates()
    )
    
    # Count total households with at least one member aged 18+ and with poultry ownership
    total_households = households_with_poultry['folio'].nunique()
    # Count households with poultry that also had dairy production
    households_with_dairy_count = households_with_dairy['folio'].nunique()
    
    # Prepare result DataFrame
    result = pd.DataFrame({
        'state': [],
        'households_with_poultry': [],
        'households_with_dairy': []
    })
    
    # Merge with portad to get state info
    households_state = pd.merge(households_with_poultry, df_portad[['folio', 'ent']], on='folio', how='left')
    
    # Group by state
    group = households_state.groupby('ent').agg(
        households_with_poultry=('folio', 'nunique')
    ).reset_index()
    
    # For households with dairy, get their state
    households_with_dairy_state = pd.merge(households_with_dairy, df_portad[['folio', 'ent']], on='folio', how='left')
    dairy_group = (
        households_with_dairy_state.groupby('ent')
        .agg(households_with_dairy=('folio', 'nunique'))
        .reset_index()
    )
    
    # Merge counts
    final_df = pd.merge(group, dairy_group, on='ent', how='left')
    final_df['ent'] = final_df['ent'].astype(int)
    final_df.rename(columns={'ent': 'state'}, inplace=True)
    
    # Map state codes to labels if needed (optional)
    # For now, keep numeric codes
    
    return final_df[['state', 'households_with_poultry', 'households_with_dairy']]