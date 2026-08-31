import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh02_1'] == 2.0)].copy()
    n3 = tables['ii_vlh'].copy()
    n4 = n3[n3['folio'].isin(n2['folio'])].copy()
    n5 = pd.DataFrame({'avg_vlh01t_no_debt': [n4['vlh01t'].mean()]})
    n6 = n1[(n1['crh02_1'] == 1.0)].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = n7[(n7['vlh18a'] > 0.0)].copy()
    n5_avg_vlh01t_no_debt_value = n5['avg_vlh01t_no_debt'].iloc[0]
    n9 = n8[n8['vlh01t'] > n5_avg_vlh01t_no_debt_value].copy()
    n10 = pd.DataFrame({'n_households': [n9['folio'].count()]})

    return n10