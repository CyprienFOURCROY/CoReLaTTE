import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_nna'].copy()
    n2 = n1[(n1['nna01'] == 1)].copy()
    n3 = tables['ii_in'].copy()
    n4 = n3[(n3['in01a10_1'] == 1)].copy()
    n5 = n4[n4['folio'].isin(n2['folio'])].copy()
    n6 = pd.DataFrame({'avg_in02a10_biz_recipients': [n5['in02a10'].mean()]})
    n6_avg_in02a10_biz_recipients_value = n6['avg_in02a10_biz_recipients'].iloc[0]
    n7 = n5[n5['in02a10'] > n6_avg_in02a10_biz_recipients_value].copy()
    n8 = n7[['folio', 'in02a10']].copy()
    n9 = n8.sort_values('in02a10', ascending=False)

    return n9