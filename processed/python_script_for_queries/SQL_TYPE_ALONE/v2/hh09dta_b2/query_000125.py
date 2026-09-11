import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(hh_size=('ls', 'count'))
    n4 = tables['ii_in'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = n5[(n5['in02a10'] > 0)].copy()
    n7 = pd.DataFrame({'oax_mean_in02a10': [n6['in02a10'].mean()]})
    n7_oax_mean_in02a10_value = n7['oax_mean_in02a10'].iloc[0]
    n8 = n6[n6['in02a10'] > n7_oax_mean_in02a10_value].copy()
    n9 = tables['ii_nna'].copy()
    n10 = n9[n9['folio'].isin(n8['folio'])].copy()
    n11 = n10[(n10['nna01'].isin([1.0, 2.0]))].copy()
    n12 = n11.merge(n3, left_on='folio', right_on='folio', how='inner')
    n13 = n12.groupby(['nna01'], as_index=False).agg(avg_hh_size=('hh_size', 'mean'))
    n14 = n13[['nna01', 'avg_hh_size']].copy()

    return n14