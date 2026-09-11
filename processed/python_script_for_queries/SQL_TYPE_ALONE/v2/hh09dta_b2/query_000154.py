import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_nna'].copy()
    n2 = n1[(n1['nna01'] == 1.0)].copy()
    n3 = tables['ii_portad'].copy()
    n4 = n3[(n3['ent'] == 20.0)].copy()
    n5 = n4[n4['folio'].isin(n2['folio'])].copy()
    n6 = pd.DataFrame({'avg_edad': [n5['edad'].mean()]})
    n7 = n5.merge(n5, left_on='ent', right_on='ent', how='inner')
    n6_avg_edad_value = n6['avg_edad'].iloc[0]
    n8 = n7[n7['edad_y'] > n6_avg_edad_value].copy()
    n9 = n8[(n8['rel_x'] == 20.0)].copy()
    n10 = pd.DataFrame({'num_pairs': [n9['folio_x'].count()]})

    return n10