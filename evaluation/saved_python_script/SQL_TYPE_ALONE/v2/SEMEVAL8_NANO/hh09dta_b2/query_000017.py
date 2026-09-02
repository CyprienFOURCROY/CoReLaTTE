def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter households with at least one adult (age >= 18)
    adults = portad[portad['edad'] >= 18]
    
    # Merge with crh to get total debts + interests
    merged = pd.merge(adults, crh[['folio', 'crh04_1', 'crh04b']], on='folio', how='inner')
    
    # Keep only records where total debts + interests is recorded (not NaN)
    debt_records = merged[merged['crh04_1'].notna() & (merged['crh04_1'] != 8)]
    
    # Calculate overall average of total debts + interests
    overall_avg_debt = debt_records['crh04b'].mean()
    
    # Filter households with debt >= overall average
    high_debt = debt_records[debt_records['crh04b'] >= overall_avg_debt]
    
    # Merge with su to get household land use info
    high_debt_su = pd.merge(high_debt, su[['folio', 'su01']], on='folio', how='left')
    
    # Map su01 to boolean for land use
    high_debt_su['uses_land'] = high_debt_su['su01'].apply(lambda x: True if x == 1 else False)
    
    # Group by land use
    result = high_debt_su.groupby('uses_land').agg(
        household_count=('folio', 'nunique'),
        average_debt=('crh04b', 'mean')
    ).reset_index()
    
    # Rename columns for clarity
    result['land_use'] = result['uses_land'].map({True: 'Yes', False: 'No'})
    result = result[['land_use', 'household_count', 'average_debt']]
    
    return result