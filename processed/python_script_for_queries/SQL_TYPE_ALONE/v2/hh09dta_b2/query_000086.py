import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh04'].isin([3.0, 4.0]))].copy()
    n3 = n2[(n2['vlh12a_c'] == 3.0)].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[['ent', 'folio', 'vlh04']].copy()
    n7 = n6.groupby(['ent'], as_index=False).agg(avg_vlh04=('vlh04', 'mean'), n_households=('folio', 'count'))
    n8 = n7[(n7['n_households'] >= 30)].copy()
    n9 = pd.DataFrame({'global_avg_vlh04': [n6['vlh04'].mean()]})
    n9_global_avg_vlh04_value = n9['global_avg_vlh04'].iloc[0]
    n10 = n8[n8['avg_vlh04'] > n9_global_avg_vlh04_value].copy()
    n11 = n10.sort_values('avg_vlh04', ascending=False)
    n12 = n11[['ent', 'avg_vlh04', 'n_households']].copy()

    return n12