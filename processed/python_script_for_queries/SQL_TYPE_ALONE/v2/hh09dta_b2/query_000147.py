import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 3.0)].copy()
    n3 = pd.DataFrame({'avg_pest_nonusers': [n2['su233'].mean()]})
    n4 = n1[(n1['su01'] == 1.0)].copy()
    n5 = tables['ii_nna'].copy()
    n6 = n5[(n5['nna01'] == 1.0)].copy()
    n7 = n4[n4['folio'].isin(n6['folio'])].copy()
    n3_avg_pest_nonusers_value = n3['avg_pest_nonusers'].iloc[0]
    n8 = n7[n7['su231'] > n3_avg_pest_nonusers_value].copy()
    n9 = n8[['folio', 'su231']].copy()
    n10 = n9.sort_values('su231', ascending=False)

    return n10