import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(total_wash_value=('ah04f_2', 'sum'))
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 1.0)].copy()
    n5 = tables['ii_se'].copy()
    n6 = n5[(n5['se01e'] == 1.0)].copy()
    n7 = n4.merge(n6, left_on='folio', right_on='folio', how='inner')
    n13 = tables['ii_portad'].copy()
    n14 = n13.groupby(['folio'], as_index=False).agg(min_ent=('ent', 'min'))
    n15 = n14[(n14['min_ent'] == 20.0)].copy()
    n16 = n7[n7['folio'].isin(n15['folio'])].copy()
    n8 = n16.merge(n2, left_on='folio', right_on='folio', how='inner')
    n9 = pd.DataFrame({'avg_wash_loss': [n8['total_wash_value'].mean()]})
    n10 = n5[(n5['se01e'] == 3.0)].copy()
    n11 = n4.merge(n10, left_on='folio', right_on='folio', how='inner')
    n17 = n11[n11['folio'].isin(n15['folio'])].copy()
    n12 = n17.merge(n2, left_on='folio', right_on='folio', how='inner')
    n9_avg_wash_loss_value = n9['avg_wash_loss'].iloc[0]
    n18 = n12[n12['total_wash_value'] > n9_avg_wash_loss_value].copy()
    n19 = pd.DataFrame({'avg_wash_no_loss_above': [n18['total_wash_value'].mean()]})

    return n19