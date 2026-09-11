import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_individuals=('ls', 'count'))
    n4 = n3[['folio']].copy()
    n5 = tables['ii_vlh'].copy()
    n6 = n5[n5['folio'].isin(n4['folio'])].copy()
    n7 = tables['ii_in'].copy()
    n8 = n7[n7['folio'].isin(n4['folio'])].copy()
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.merge(n6, left_on='folio', right_on='folio', how='inner')
    n11 = n10[(n10['in02a10'] > 0.0)].copy()
    n12 = pd.DataFrame({'avg_in02a10': [n11['in02a10'].mean()]})
    n13 = n11[(n11['vlh04_x'].isin([1.0, 2.0])) & (n11['vlh01l_y'].isin([1.0, 2.0]))].copy()
    n12_avg_in02a10_value = n12['avg_in02a10'].iloc[0]
    n14 = n13[n13['in02a10'] > n12_avg_in02a10_value].copy()
    n15 = pd.DataFrame({'n_households_above_avg': [n14['folio'].count()]})
    n16 = n15[['n_households_above_avg']].copy()

    return n16