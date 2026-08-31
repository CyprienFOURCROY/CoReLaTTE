import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03h'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(members_with_fin_assets=('ah03h', 'count'))
    n4 = tables['ii_vlh'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = tables['ii_nna'].copy()
    n7 = n6[(n6['nna01'] == 2.0)].copy()
    n8 = n7.merge(n4, left_on='folio', right_on='folio', how='inner')
    n9 = pd.DataFrame({'avg_vlh18a_no_nonag': [n8['vlh18a'].mean()]})
    n9_avg_vlh18a_no_nonag_value = n9['avg_vlh18a_no_nonag'].iloc[0]
    n10 = n5[n5['vlh18a'] > n9_avg_vlh18a_no_nonag_value].copy()
    n11 = n10[['folio', 'vlh18a']].copy()

    return n11