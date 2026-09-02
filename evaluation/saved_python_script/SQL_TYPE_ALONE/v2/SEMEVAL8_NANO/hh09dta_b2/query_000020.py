def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    inr = tables["ii_inr"]
    
    # Merge tables on 'folio'
    merged = portad.merge(nna, on='folio', how='inner').merge(inr, on='folio', how='inner')
    
    # Filter households that produced or sold eggs last 12 months
    eggs_mask = merged['inr02d'] == 1  # 'inr02d' indicates produce/sell eggs last 12 months
    filtered = merged[eggs_mask]
    
    # Filter households that own/share a non-agricultural business
    nna_mask = merged['nna01'] == 1  # 'nna01' indicates owns/shares non-ag business
    filtered_both = filtered[filtered['folio'].isin(merged[nna_mask]['folio'])]
    
    # Group by 'ent' (state) and count households
    result = (
        filtered_both
        .groupby(['ent'])
        .agg(household_count=('folio', 'nunique'),
             household_size=('edad', 'count'))
        .reset_index()
    )
    
    # Find the state with the highest number of households
    max_idx = result['household_count'].idxmax()
    state_code = result.loc[max_idx, 'ent']
    household_count = result.loc[max_idx, 'household_count']
    household_size = result.loc[max_idx, 'household_size']
    
    # Return as DataFrame
    return pd.DataFrame({
        'state_code': [state_code],
        'household_count': [household_count],
        'household_size': [household_size]
    })