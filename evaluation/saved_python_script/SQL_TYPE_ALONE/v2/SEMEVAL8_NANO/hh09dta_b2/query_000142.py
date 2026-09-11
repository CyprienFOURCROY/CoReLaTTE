def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]
    df_nna_enriched = tables["ii_nna_enriched"]
    df_se_enriched = tables["ii_se_enriched"]
    df_ah_enriched = tables["ii_ah_enriched"]
    df_portad_enriched = tables["ii_portad_enriched"]
    df_vlh_enriched = tables["ii_vlh_enriched"]
    
    # Filter households that own or share a non-agricultural business
    nna_mask = df_nna['nna01'].isin([1, 2])
    nna_households = df_nna[nna_mask]['folio']
    
    # Merge with portad to get household info
    portad_nna = df_portad[df_portad['folio'].isin(nna_households)]
    
    # Merge with ah to get safety info
    ah_mask = portad_nna['folio'].isin(df_ah['folio'])
    portad_ah = portad_nna[ah_mask].merge(df_ah, on='folio', how='left')
    
    # Filter households that report feeling unsafe or very unsafe at home
    safety_mask = portad_ah['vlh04'].isin([3, 4])  # 3: Unsafe, 4: Very unsafe
    unsafe_households = portad_ah[safety_mask]
    
    # Merge with vlh to get total times robbed since 2005
    vlh_mask = unsafe_households['folio'].isin(df_vlh['folio'])
    households_vlh = unsafe_households[vlh_mask].merge(df_vlh, on='folio', how='left')
    
    # Calculate the average total times robbed since 2005 for this group
    # Use 'vlh18a' as total times entered/robbed since 2005
    # Some entries may be NaN, treat them as 0 for average calculation
    total_times = households_vlh['vlh18a'].fillna(0)
    average_times = total_times.mean()
    
    # Filter households with total times since 2005 above the group average
    above_avg_mask = total_times > average_times
    result_df = households_vlh[above_avg_mask]
    
    # Select relevant columns and sort from highest to lowest
    final_df = result_df[['folio', 'vlh04', 'vlh18a']].copy()
    final_df = final_df.rename(columns={'vlh04': 'Safety_Response', 'vlh18a': 'Times_Robbed_Since_2005'})
    final_df = final_df.sort_values(by='Times_Robbed_Since_2005', ascending=False).reset_index(drop=True)
    
    return final_df