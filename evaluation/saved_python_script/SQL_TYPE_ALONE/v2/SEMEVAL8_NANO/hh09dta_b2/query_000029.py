def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]
    df_se = tables["ii_se"]
    
    # Filter households with age info
    portad_filtered = df_portad[['folio', 'edad', 'ent', 'rel']].copy()
    portad_filtered = portad_filtered.dropna(subset=['edad'])
    
    # Filter households that feel unsafe or very unsafe at home
    # 'vlh04' column: 3: Unsafe, 4: Very unsafe
    # Merge with household info
    households_safety = portad_filtered.merge(df_vlh[['folio', 'vlh04']], on='folio', how='inner')
    households_safety = households_safety[households_safety['vlh04'].isin([3, 4])]
    
    # Filter households that received Liconsa milk in last 12 months
    in_last12 = df_in[['folio', 'in03a']].copy()
    in_last12 = in_last12[in_last12['in03a'] == 1]
    
    # Filter households with positive amount from 'Other Government Program'
    # 'in02a10' > 0
    in_other_gov = df_in[['folio', 'in02a10']].copy()
    in_other_gov = in_other_gov[in_other_gov['in02a10'] > 0]
    
    # Filter households with total break-ins since 2005 > overall average
    # 'vlh12a' (break-ins since 2005)
    vlh_breakins = df_vlh[['folio', 'vlh12a']].copy()
    # Drop NaNs
    vlh_breakins = vlh_breakins.dropna(subset=['vlh12a'])
    overall_avg_breakins = vlh_breakins['vlh12a'].mean()
    vlh_breakins_above_avg = vlh_breakins[vlh_breakins['vlh12a'] > overall_avg_breakins]
    
    # Merge all filters
    merged = portad_filtered.merge(households_safety[['folio']], on='folio', how='inner')
    merged = merged.merge(in_last12[['folio']], on='folio', how='inner')
    merged = merged.merge(in_other_gov[['folio']], on='folio', how='inner')
    merged = merged.merge(vlh_breakins_above_avg[['folio']], on='folio', how='inner')
    
    # For each household, compute:
    # - average age
    # - number of adults (18+)
    # Merge with age info
    household_ages = merged.merge(df_portad[['folio', 'edad']], on='folio', how='left')
    # Drop NaN ages
    household_ages = household_ages.dropna(subset=['edad'])
    # Group by 'ent' (state)
    result = household_ages.groupby('ent').agg(
        average_age=('edad', 'mean'),
        adults_18_plus=('edad', lambda x: (x >= 18).sum())
    ).reset_index()
    # Rank by highest average age
    result = result.sort_values(by='average_age', ascending=False).reset_index(drop=True)
    return result