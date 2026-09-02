def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]
    
    # Filter households with at least one member aged 65 or older
    elderly_members = df_portad[df_portad['edad'] >= 65]
    households_with_elderly = elderly_members['folio'].unique()
    
    # Filter households in df_crh with total debts + interests reported (not null) and in households_with_elderly
    df_crh_filtered = df_crh[
        (df_crh['folio'].isin(households_with_elderly)) &
        (df_crh['crh04_1'].notnull()) &
        (df_crh['crh04_1'] != 8)  # Exclude DK if needed, but here just check not null
    ]
    
    # Calculate average total debts + interests for elderly households
    avg_debt = df_crh_filtered['crh04_2'].mean()
    
    # Filter households with total debts > average
    households_high_debt = df_crh_filtered[
        df_crh_filtered['crh04_2'] > avg_debt
    ][['folio', 'crh04_2', 'crh02b']]
    
    # Filter households that received a positive amount from Other Government Program
    # In df_in, the relevant columns are 'in02a10' (amount received directly)
    # and 'in01a10_1' (participation indicator). But from the description, 'in02a10' is amount received directly.
    # We need to find households with amount > 0 in 'in02a10' and participation indicator not DK or None.
    df_in_filtered = df_in[
        (df_in['folio'].isin(households_high_debt['folio'])) &
        (df_in['in02a10'] > 0)
    ][['folio', 'in02a10']]
    
    # Merge to get households with positive amount from Other Government Program
    result = households_high_debt.merge(df_in_filtered, on='folio', how='inner')
    
    # Select and sort by debt descending
    result_sorted = result[['folio', 'crh04_2', 'in02a10']].sort_values(by='crh04_2', ascending=False)
    
    # Rename columns for clarity
    result_sorted = result_sorted.rename(columns={
        'crh04_2': 'Total_Debt_Pesos',
        'in02a10': 'Other_Gov_Program_Amount'
    })
    
    return result_sorted.reset_index(drop=True)