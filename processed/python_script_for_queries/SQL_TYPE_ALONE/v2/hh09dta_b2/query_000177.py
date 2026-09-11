import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent_min=('ent', 'min'))
    n3 = n2[(n2['ent_min'] == 20.0)].copy()
    n4 = n3[['folio']].copy()
    n5 = n2[(n2['ent_min'] != 20.0)].copy()
    n6 = n5[['folio']].copy()
    n7 = tables['ii_crh'].copy()
    n8 = n7[(n7['crh04_1'] == 1.0)].copy()
    n9 = n8[n8['folio'].isin(n6['folio'])].copy()
    n10 = tables['ii_in'].copy()
    n11 = n9.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11[(n11['in02a10'] > 0.0)].copy()
    n13 = pd.DataFrame({'avg_outside_in02a10': [n12['in02a10'].mean()]})
    n14 = n8[n8['folio'].isin(n4['folio'])].copy()
    n15 = n14.merge(n10, left_on='folio', right_on='folio', how='inner')
    n16 = n15[(n15['in02a10'] > 0.0)].copy()
    n13_avg_outside_in02a10_value = n13['avg_outside_in02a10'].iloc[0]
    n17 = n16[n16['in02a10'] >= n13_avg_outside_in02a10_value].copy()
    n18 = n17[['folio', 'crh04_2', 'in02a10']].copy()

    return n18