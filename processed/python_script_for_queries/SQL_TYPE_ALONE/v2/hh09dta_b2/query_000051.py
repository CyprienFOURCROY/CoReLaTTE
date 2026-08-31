import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh04'].isin([3.0, 4.0]))].copy()
    n3 = tables['ii_nna'].copy()
    n4 = n3[(n3['nna01'] == 1.0)].copy()
    n5 = n2[~n2['folio'].isin(n4['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n10 = n9[(n9['n_households'] >= 30)].copy()
    n11 = pd.DataFrame({'avg_state_count': [n10['n_households'].mean()]})
    n11_avg_state_count_value = n11['avg_state_count'].iloc[0]
    n12 = n10[n10['n_households'] >= n11_avg_state_count_value].copy()
    n13 = n12.sort_values('n_households', ascending=False)
    n14 = n13[['ent', 'n_households']].copy()

    return n14