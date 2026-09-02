def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter adults (age >= 18)
    adults = portad[portad['edad'] >= 18]
    
    # Filter households that use a plot for farming (su01 == 1)
    su_farming = su[su['su01'] == 1]
    
    # Merge adults with household info
    adults_households = pd.merge(adults, su_farming[['folio']], on='folio', how='inner')
    
    # Merge with household debt info
    debt_info = crh[['folio', 'crh04_2']]
    merged = pd.merge(adults_households, debt_info, on='folio', how='inner')
    
    # Filter for positive total debt (crh04_2 > 0)
    debt_positive = merged[merged['crh04_2'] > 0]
    
    # Map 'ent' to state names for clarity (optional, not required for output)
    # But since only state codes are needed, we keep 'ent' as is.
    
    # Group by 'ent' (state), compute mean of 'crh04_2' and count of records
    result = (
        debt_positive
        .groupby('ent')
        .agg(
            average_debt=('crh04_2', 'mean'),
            count_records=('folio', 'count')
        )
        .reset_index()
    )
    
    # Get top 10 states with highest average household debt
    top10 = result.sort_values(by='average_debt', ascending=False).head(10)
    
    # Map 'ent' codes to state names for clarity (optional)
    state_mapping = {
        2: 'Baja California',
        3: 'Baja California Sur',
        4: 'Campeche',
        5: 'Coahuila',
        6: 'Colima',
        7: 'Chiapas',
        9: 'Distrito Federal',
        10: 'Durango',
        11: 'Guanajuato',
        12: 'Guerrero',
        13: 'Hidalgo',
        14: 'Jalisco',
        15: 'Estado de México',
        16: 'Michoacán',
        17: 'Morelos',
        18: 'Nayarit',
        19: 'Nuevo León',
        20: 'Oaxaca',
        21: 'Puebla',
        22: 'Querétaro',
        25: 'Sinaloa',
        26: 'Sonora',
        28: 'Tamaulipas',
        29: 'Tlaxcala',
        30: 'Veracruz',
        31: 'Yucatán',
        32: 'Zacatecas'
    }
    top10['state_name'] = top10['ent'].map(state_mapping)
    
    # Select final columns
    final_df = top10[['state_name', 'average_debt', 'count_records']]
    final_df.columns = ['State', 'Average Household Debt (Pesos)', 'Number of Adults']
    
    return final_df