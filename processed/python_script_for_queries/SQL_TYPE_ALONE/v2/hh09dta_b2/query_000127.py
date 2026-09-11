import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01a'] == 3.0) & (n1['se01b'] == 3.0) & (n1['se01c'] == 3.0) & (n1['se01d'] == 3.0) & (n1['se01e'] == 3.0) & (n1['se01f'] == 3.0)].copy()
    n3 = tables['ii_vlh'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = pd.DataFrame({'avg_vlh18a_shock_free': [n4['vlh18a'].mean()]})
    n6 = n1[~n1['folio'].isin(n2['folio'])].copy()
    n7 = n6.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5_avg_vlh18a_shock_free_value = n5['avg_vlh18a_shock_free'].iloc[0]
    n8 = n7[n7['vlh18a'] > n5_avg_vlh18a_shock_free_value].copy()
    n9 = n8[['folio', 'vlh18a']].copy()

    return n9