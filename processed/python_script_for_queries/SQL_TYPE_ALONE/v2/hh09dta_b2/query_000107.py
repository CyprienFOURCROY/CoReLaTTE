import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 65.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_in'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = n5[(n5['in01a11_1'] == 1.0) & (n5['in02a11'] > 0.0)].copy()
    n7 = n6[(n6['in03a'] == 1.0)].copy()
    n8 = pd.DataFrame({'avg_in02a11_liconsa_65plus': [n7['in02a11'].mean()]})
    n8_avg_in02a11_liconsa_65plus_value = n8['avg_in02a11_liconsa_65plus'].iloc[0]
    n9 = n6[n6['in02a11'] > n8_avg_in02a11_liconsa_65plus_value].copy()
    n10 = n9.sort_values('in02a11', ascending=False)
    n11 = n10[['folio', 'in02a11']].copy()

    return n11