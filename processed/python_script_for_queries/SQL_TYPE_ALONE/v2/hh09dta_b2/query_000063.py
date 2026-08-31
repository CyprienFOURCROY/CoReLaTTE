import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20) & (n1['edad'] >= 18)].copy()
    n3 = tables['ii_nna'].copy()
    n4 = n3[(n3['nna01'] == 1)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = pd.DataFrame({'avg_age': [n5['edad'].mean()]})
    n6_avg_age_value = n6['avg_age'].iloc[0]
    n7 = n5[n5['edad'] > n6_avg_age_value].copy()
    n8 = tables['ii_in'].copy()
    n9 = n7.merge(n8, left_on='folio_x', right_on='folio', how='inner')
    n10 = n9[(n9['in02a10'] > 0)].copy()
    n11 = pd.DataFrame({'n_individuals_above_avg_with_benefit': [n10['in02a10'].count()]})

    return n11