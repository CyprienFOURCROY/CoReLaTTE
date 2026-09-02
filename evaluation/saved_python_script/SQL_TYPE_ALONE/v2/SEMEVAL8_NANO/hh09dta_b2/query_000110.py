def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    inr = tables["ii_inr"]
    se = tables["ii_se"]
    in_enriched = tables["ii_in_enriched"]
    se_enriched = tables["ii_se_enriched"]
    
    # Filter households that use a plot/land for showing/farming/vegetable
    su_use_plot = su[su['su01'] == 1]
    
    # Merge with portad to get household info
    merged = pd.merge(su_use_plot[['folio']], portad, on='folio', how='inner')
    
    # Merge with inr to get crop info
    merged = pd.merge(merged, inr[['folio', 'inr02c']], on='folio', how='left')
    
    # Merge with se to get total crop loss info
    merged = pd.merge(merged, se[['folio', 'se01e']], on='folio', how='left')
    
    # Merge with in_enriched to get 'in01a11_1' (participation in '70 y más')
    merged = pd.merge(merged, in_enriched[['folio', 'in01a11_1']], on='folio', how='left')
    
    # Merge with se_enriched to get 'se01e' info
    merged = pd.merge(merged, se_enriched[['folio', 'se01e']], on='folio', how='left')
    
    # Filter for households that experienced total crop loss in last 5 years
    crop_loss_mask = merged['se01e'] == 1
    
    # Filter for households that have no members participating in any 'Other Government Program'
    # 'inr' columns for 'Other Government Program' are 'inr02a10' and 'inr02a10' in enriched
    # But in the schema, 'inr02a10' is the amount received directly, and 'inr02a10' in enriched is participation
    # Actually, participation is indicated by 'inr02a10' in the original data, but in enriched, participation is in 'in01a10_1'
    # So, check 'in01a10_1' == 3 (no participation)
    # Merge with in_enriched for 'in01a10_1'
    merged = pd.merge(merged, in_enriched[['folio', 'in01a10_1']], on='folio', how='left')
    no_other_gov_mask = merged['in01a10_1'] == 3
    
    # Apply all filters
    filtered = merged[crop_loss_mask & no_other_gov_mask]
    
    # For each household, count number of adults (age >= 18)
    # Merge with portad to get 'edad'
    filtered = pd.merge(filtered, portad[['folio', 'edad']], on='folio', how='left')
    filtered['is_adult'] = filtered['edad'] >= 18
    adult_counts = filtered.groupby('folio')['is_adult'].sum().reset_index()
    adult_counts.rename(columns={'is_adult': 'adult_count'}, inplace=True)
    
    # Merge back to get 'inr02c' (crop loss expense in fertilizer)
    # Already merged, so get 'inr02c' and 'adult_count'
    result = pd.merge(filtered[['folio', 'inr02c']], adult_counts, on='folio', how='left')
    
    # Filter for households with crop loss expense in fertilizer (assuming non-null and > 0)
    # But in the sample, expenses are in 'inr02c' as value in pesos, possibly NaN
    # Filter for non-NaN and > 0
    result = result[result['inr02c'].notna() & (result['inr02c'] > 0)]
    
    # Group by adult_count and compute mean expense
    group = result.groupby('adult_count')['inr02c'].mean().reset_index()
    group.rename(columns={'inr02c': 'avg_fertilizer_expense'}, inplace=True)
    
    # Count households per adult_count
    household_counts = result.groupby('adult_count')['folio'].nunique().reset_index()
    household_counts.rename(columns={'folio': 'household_count'}, inplace=True)
    
    # Merge results
    final = pd.merge(group, household_counts, on='adult_count')
    
    # Return as DataFrame
    return final