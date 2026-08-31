import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in02a10'] > 0.0)].copy()
    n3 = tables['ii_nna'].copy()
    n4 = n3[(n3['nna01'] == 1.0)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = tables['ii_su'].copy()
    n7 = n6[(n6['su01'] == 1.0)].copy()
    n8 = n5[n5['folio'].isin(n7['folio'])].copy()
    n9 = tables['ii_in'].copy()
    n10 = n9[(n9['in02a10'] > 0.0)].copy()
    n11 = tables['ii_nna'].copy()
    n12 = n11[(n11['nna01'] == 1.0)].copy()
    n13 = n10[n10['folio'].isin(n12['folio'])].copy()
    n14 = tables['ii_su'].copy()
    n15 = n14[(n14['su01'] == 1.0)].copy()
    n16 = n13[n13['folio'].isin(n15['folio'])].copy()
    n17 = pd.DataFrame({'avg_in02a10': [n16['in02a10'].mean()]})
    n17_avg_in02a10_value = n17['avg_in02a10'].iloc[0]
    n18 = n8[n8['in02a10'] > n17_avg_in02a10_value].copy()
    n19 = n18[['folio', 'in02a10']].copy()
    n20 = n19.sort_values('in02a10', ascending=False)

    return n20