import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in02a10'] > 0)].copy()
    n3 = tables['ii_portad'].copy()
    n4 = n3[(n3['ent'].isin([20.0, 21.0]))].copy()
    n5 = tables['ii_su'].copy()
    n6 = n5[(n5['su01'] == 1.0)].copy()
    n7 = tables['ii_nna'].copy()
    n8 = n7[(n7['nna01'] == 1.0)].copy()
    n9 = n2[n2['folio'].isin(n4['folio'])].copy()
    n10 = n9[n9['folio'].isin(n6['folio'])].copy()
    n11 = n10[n10['folio'].isin(n8['folio'])].copy()
    n12 = n2[n2['folio'].isin(n4['folio'])].copy()
    n13 = n12[n12['folio'].isin(n6['folio'])].copy()
    n14 = pd.DataFrame({'avg_in02a10': [n13['in02a10'].mean()]})
    n14_avg_in02a10_value = n14['avg_in02a10'].iloc[0]
    n15 = n11[n11['in02a10'] > n14_avg_in02a10_value].copy()
    n16 = n15[['folio', 'in02a10']].copy()
    n17 = n16.sort_values('in02a10', ascending=False)

    return n17