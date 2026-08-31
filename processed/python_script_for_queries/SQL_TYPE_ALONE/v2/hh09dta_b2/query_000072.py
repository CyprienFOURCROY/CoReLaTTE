import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_vlh'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = n5[(n5['vlh04'].isin([3.0, 4.0]))].copy()
    n7 = pd.DataFrame({'avg_vlh18a_unsafe_oax': [n6['vlh18a'].mean()]})
    n8 = n2[(n2['edad'] >= 18.0)].copy()
    n9 = n8[['folio', 'ls', 'edad', 'ent']].copy()
    n10 = n9.merge(n6, left_on='folio', right_on='folio', how='inner')
    n7_avg_vlh18a_unsafe_oax_value = n7['avg_vlh18a_unsafe_oax'].iloc[0]
    n11 = n10[n10['vlh18a'] > n7_avg_vlh18a_unsafe_oax_value].copy()
    n12 = n11[['folio', 'ls', 'edad', 'ent', 'vlh04', 'vlh18a']].copy()

    return n12