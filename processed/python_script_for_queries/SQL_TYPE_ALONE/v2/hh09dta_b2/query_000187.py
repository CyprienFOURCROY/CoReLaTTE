import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in01a10_1'] == 1.0)].copy()
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 1.0)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[(n5['in02a10'] > 0)].copy()
    n7 = pd.DataFrame({'avg_in02a10': [n6['in02a10'].mean()]})
    n8 = n5[(n5['in02a10'] > 0)].copy()
    n7_avg_in02a10_value = n7['avg_in02a10'].iloc[0]
    n9 = n8[n8['in02a10'] > n7_avg_in02a10_value].copy()
    n10 = n9[['folio', 'in02a10']].copy()

    return n10