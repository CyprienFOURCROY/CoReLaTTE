import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n3[(n3['ls'] == 1.0) & (n3['ah04e_1'] == 1.0) & (n3['ah04e_2'] > 0.0)].copy()
    n5 = tables['ii_vlh'].copy()
    n6 = n5[(n5['vlh12a_c'] == 3.0)].copy()
    n7 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['ls_x'] == '01') & (n7['edad'] >= 18.0)].copy()
    n9 = n8.merge(n6, left_on='folio', right_on='folio', how='inner')
    n10 = pd.DataFrame({'global_avg_value': [n9['ah04e_2'].mean()]})
    n10_global_avg_value_value = n10['global_avg_value'].iloc[0]
    n11 = n9[n9['ah04e_2'] > n10_global_avg_value_value].copy()
    n12 = pd.DataFrame({'num_heads_above_avg': [n11['folio'].count()], 'avg_age': [n11['edad'].mean()]})

    return n12