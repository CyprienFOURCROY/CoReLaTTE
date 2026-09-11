import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh02_1'] == 1)].copy()
    n3 = n2[['folio', 'crh02_2']].copy()
    n4 = tables['ii_vlh'].copy()
    n5 = n4[['folio', 'vlh18a']].copy()
    n6 = n3.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n4[(n4['vlh18a'] > 0)].copy()
    n8 = pd.DataFrame({'avg_vlh18a': [n7['vlh18a'].mean()]})
    n8_avg_vlh18a_value = n8['avg_vlh18a'].iloc[0]
    n9 = n6[n6['vlh18a'] > n8_avg_vlh18a_value].copy()
    n10 = n9[['folio', 'vlh18a', 'crh02_2']].copy()

    return n10