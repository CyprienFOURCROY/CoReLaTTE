def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    nna = tables["ii_nna"]
    se = tables["ii_se"]
    
    # Filter for adults (edad > 18)
    adults = portad[portad['edad'] > 18]
    
    # Calculate overall average age among adults
    overall_avg_age = adults['edad'].mean()
    
    # Merge tables on 'folio'
    merged = adults.merge(su, on='folio', how='inner') \
                   .merge(nna, on='folio', how='inner') \
                   .merge(se, on='folio', how='inner')
    
    # Apply filters:
    # 1. Age above overall average
    filtered = merged[merged['edad'] > overall_avg_age]
    
    # 2. Household uses land for farming (su01 == 1)
    filtered = filtered[filtered['su01'] == 1]
    
    # 3. Total crop loss in last five years (se01e == 1)
    filtered = filtered[filtered['se01e'] == 1]
    
    # 4. Has a non-agricultural business (nna01 == 1)
    filtered = filtered[filtered['nna01'] == 1]
    
    # Count number of such individuals per state ('ent')
    count_per_state = filtered.groupby('ent').size().reset_index(name='count')
    
    # Calculate average household expense on seeds ('seu234')
    # First, merge again to get 'seu234' from 'se'
    # Already merged, so 'seu234' is present
    # Filter out NaN in 'seu234'
    seed_expenses = filtered['seu234'].dropna()
    avg_seed_expense = seed_expenses.mean() if not seed_expenses.empty else float('nan')
    
    # Prepare result DataFrame
    result = count_per_state.copy()
    result['average_seed_expense'] = avg_seed_expense
    
    return result