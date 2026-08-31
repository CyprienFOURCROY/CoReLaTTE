import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1)].copy()
    n3 = tables['ii_in'].copy()
    n4 = n3[(n3['in02a10'] > 0)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6[['folio', 'ent']].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n9 = n5.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n11 = n10[(n10['n_households'] >= 50)].copy()
    n12 = pd.DataFrame({'avg_n_households': [n11['n_households'].mean()]})
    n12_avg_n_households_value = n12['avg_n_households'].iloc[0]
    n13 = n11[n11['n_households'] > n12_avg_n_households_value].copy()
    n14 = n13.sort_values('n_households', ascending=False)

    return n14