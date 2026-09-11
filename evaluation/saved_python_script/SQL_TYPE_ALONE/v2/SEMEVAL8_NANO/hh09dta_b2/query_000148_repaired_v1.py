def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    in_table = tables["ii_in"]
    inr_table = tables["ii_inr"]
    
    # Merge portad with crh and in on 'folio'
    df = portad.merge(crh, on='folio', how='inner').merge(in_table, on='folio', how='inner').merge(inr_table, on='folio', how='inner')
    
    # Filter households with at least one member aged 60 or older who feel unsafe or very unsafe at home
    age_filter = df['edad'] >= 60
    safety_filter = df['vlh04'].isin([3,4])  # 3: Unsafe, 4: Very unsafe
    df_filtered = df[age_filter & safety_filter]
    
    # Calculate total household debt (debts + interest)
    # Handle NaNs: treat NaN as zero for sum
    df_filtered['total_debt'] = df_filtered['crh04_2'].fillna(0)
    
    # Group by 'ent' (state) and compute average total debt
    state_debt_avg = df_filtered.groupby('ent')['total_debt'].mean()
    
    # Compute overall average for this group
    overall_avg = state_debt_avg.mean()
    
    # Select states with average >= overall average
    states_above_avg = state_debt_avg[state_debt_avg >= overall_avg]
    
    # Find the state with the highest average total debt
    max_state = states_above_avg.idxmax()
    max_avg = states_above_avg.max()
    
    # Return as DataFrame
    return pd.DataFrame(
        {"state": [max_state], "average_total_debt": [max_avg]}
    )