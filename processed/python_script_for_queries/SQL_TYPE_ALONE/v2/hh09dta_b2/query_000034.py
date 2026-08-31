import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = tables['ii_in'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3[(n3['in03a_x'] == 1) & (n3['in01a10_1_x'] == 1) & (n3['in03b_y'] == 3)].copy()
    n5 = n4[['folio', 'in02a10_y']].copy()
    n6 = tables['ii_nna'].copy()
    n7 = n6[(n6['nna01'] == 1)].copy()
    n8 = n5[n5['folio'].isin(n7['folio'])].copy()
    n9 = tables['ii_portad'].copy()
    n10 = n8.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = pd.DataFrame({'global_avg_in02a10': [n10['in02a10_y'].mean()]})
    n11_global_avg_in02a10_value = n11['global_avg_in02a10'].iloc[0]
    n12 = n10[n10['in02a10_y'] > n11_global_avg_in02a10_value].copy()
    n13 = tables['ii_crh'].copy()
    n14 = n12.merge(n13, left_on='folio', right_on='folio', how='inner')
    n15 = n14.groupby(['ent'], as_index=False).agg(total_households=('folio', 'count'))
    n16 = n14[(n14['crh03_1'] == 1) & (n14['crh03_2'] > 0)].copy()
    n17 = n16.groupby(['ent'], as_index=False).agg(paid_households=('folio', 'count'))
    n18 = n15.merge(n17, left_on='ent', right_on='ent', how='left')
    n19 = n18[['ent', 'total_households', 'paid_households']].copy()

    return n19