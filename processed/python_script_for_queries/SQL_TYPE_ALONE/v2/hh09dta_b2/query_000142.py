import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh04'].isin([3.0, 4.0]))].copy()
    n3 = tables['ii_nna'].copy()
    n4 = n3[(n3['nna01'] == 1.0)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = pd.DataFrame({'avg_vlh18a': [n5['vlh18a'].mean()]})
    n6_avg_vlh18a_value = n6['avg_vlh18a'].iloc[0]
    n7 = n5[n5['vlh18a'] > n6_avg_vlh18a_value].copy()
    n8 = n7[['folio', 'vlh18a', 'vlh04']].copy()
    n9 = n8.sort_values('vlh18a', ascending=False)

    return n9