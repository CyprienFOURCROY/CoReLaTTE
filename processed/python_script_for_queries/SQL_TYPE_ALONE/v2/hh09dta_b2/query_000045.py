import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01a'] == 1)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(total_washstove_value=('ah04f_2', 'sum'))
    n5 = pd.DataFrame({'mean_total_washstove_value': [n4['total_washstove_value'].mean()]})
    n5_mean_total_washstove_value_value = n5['mean_total_washstove_value'].iloc[0]
    n6 = n4[n4['total_washstove_value'] > n5_mean_total_washstove_value_value].copy()
    n7 = n6[n6['folio'].isin(n2['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8[(n8['edad'] >= 60)].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(elder_count=('ls', 'count'))
    n11 = n7[n7['folio'].isin(n10['folio'])].copy()
    n12 = pd.DataFrame({'households_with_elder': [n11['folio'].count()]})

    return n12