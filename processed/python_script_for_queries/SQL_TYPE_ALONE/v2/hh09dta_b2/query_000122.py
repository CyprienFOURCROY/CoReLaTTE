import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(max_ent=('ent', 'max'))
    n3 = n2[(n2['max_ent'] == 20.0)].copy()
    n4 = n3[['folio']].copy()
    n5 = tables['ii_in'].copy()
    n6 = n5[(n5['in01a10_1'] == 1.0) & (n5['in02a10'] != None)].copy()
    n7 = pd.DataFrame({'avg_in02a10_receivers': [n6['in02a10'].mean()]})
    n8 = n6[n6['folio'].isin(n4['folio'])].copy()
    n7_avg_in02a10_receivers_value = n7['avg_in02a10_receivers'].iloc[0]
    n9 = n8[n8['in02a10'] > n7_avg_in02a10_receivers_value].copy()
    n10 = n9[['folio', 'in02a10']].copy()

    return n10