def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]
    df_ah = tables["ii_ah"]
    
    # Filter households with at least one member aged 60 or older
    households_age_60_plus = df_portad[df_portad['edad'] >= 60]['folio'].unique()
    
    # Filter households with at least one member with positive value of financial assets/afores
    households_fin_assets = df_ah[df_ah['ah04h_1'] == 1]['folio'].unique()
    
    # Filter households with total debts plus interests above the overall average
    # First, get total debts plus interests
    total_debts = df_crh[['folio', 'crh04_1', 'crh04_2']].dropna()
    total_debts['debt_value'] = total_debts['crh04_2']
    # Filter out DK (value 8) or missing
    total_debts = total_debts[total_debts['crh04_1'] != 8]
    # Compute overall average
    overall_avg_debt = total_debts['debt_value'].mean()
    # Filter households above average
    households_above_avg_debt = total_debts[total_debts['debt_value'] > overall_avg_debt]['folio'].unique()
    
    # Find households satisfying all three conditions
    households_condition = set(households_age_60_plus) & set(households_fin_assets) & set(households_above_avg_debt)
    
    # Among these households, count how many received any direct income from the Other Government Program
    # Filter in table for households in the set
    df_in_filtered = df_in[df_in['folio'].isin(households_condition)]
    # Check if any member received income from the program (columns in ii_in_enriched.txt)
    # 'in02a10' indicates amount received directly from Other Government Program
    # We consider any non-NaN, non-zero value as received income
    received_income_mask = df_in_filtered['in02a10'].notna() & (df_in_filtered['in02a10'] > 0)
    households_received_income = df_in_filtered[received_income_mask]['folio'].unique()
    
    # Count households satisfying the condition
    result_count = len(households_received_income)
    
    return pd.DataFrame({"count": [result_count]})