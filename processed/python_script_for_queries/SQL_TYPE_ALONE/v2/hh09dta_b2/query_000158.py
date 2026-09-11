import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(adult_member_rows=('ls', 'count'))
    n4 = tables['ii_in'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[(n5['in01a10_1'] == 1.0) & (n5['in02a10'] > 0.0)].copy()
    n7 = tables['ii_vlh'].copy()
    n8 = n7[n7['folio'].isin(n3['folio'])].copy()
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = pd.DataFrame({'avg_in02a10': [n6['in02a10'].mean()]})
    n10_avg_in02a10_value = n10['avg_in02a10'].iloc[0]
    n11 = n9[n9['in02a10'] > n10_avg_in02a10_value].copy()
    n12 = n11[(n11['vlh04'].isin([1.0, 2.0]))].copy()
    n13 = pd.DataFrame({'households_count': [n12['folio'].count()]})

    return n13