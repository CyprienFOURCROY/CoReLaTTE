def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter households that use a plot/land for farming/vegetables and report positive total debt
    # 1. Households that use land for farming/vegetables: su['su01'] == 1
    # 2. Households with total debt > 0: crh['crh04_1'] == 1 and crh['crh04_2'] > 0
    
    # Merge su and crh on 'folio'
    merged = pd.merge(su, crh, on='folio', how='inner')
    
    # Filter for land use and positive total debt
    filtered = merged[
        (merged['su01'] == 1) &
        (merged['crh04_1'] == 1) &
        (merged['crh04_2'] > 0)
    ]
    
    # Merge with portad to get 'edad' (age), 'ent' (state), 'rel' (result interview)
    merged_full = pd.merge(filtered, portad, on='folio', how='inner')
    
    # Group by 'ent' (state)
    group = merged_full.groupby('ent')
    
    # Calculate average total debt and average household size per state
    result = group.agg(
        average_total_debt=('crh04_2', 'mean'),
        average_household_size=('su03', 'mean'),
        household_count=('folio', 'count')
    ).reset_index()
    
    # Rank by average total debt descending
    result_sorted = result.sort_values(by='average_total_debt', ascending=False).reset_index(drop=True)
    
    # Select relevant columns
    final = result_sorted[['ent', 'average_total_debt', 'average_household_size', 'household_count']]
    
    return final