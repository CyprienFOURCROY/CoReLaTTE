import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20) & (n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(adult_member_count=('folio', 'count'))
    n4 = n3[['folio']].copy()
    n5 = tables['ii_ah'].copy()
    n6 = n5[(n5['ah03e'] == 1) & (n5['ah04e_1'] == 1)].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(total_e_value=('ah04e_2', 'sum'))
    n8 = n4[n4['folio'].isin(n7['folio'])].copy()
    n9 = n8.merge(n7, left_on='folio', right_on='folio', how='inner')
    n10 = pd.DataFrame({'avg_total_e_value': [n9['total_e_value'].mean()]})
    n11 = tables['ii_inr'].copy()
    n12 = n11[(n11['inr02f'] == 1)].copy()
    n13 = n12.groupby(['folio'], as_index=False).agg(crafts_member_count=('folio', 'count'))
    n14 = n4[n4['folio'].isin(n13['folio'])].copy()
    n15 = n14[n14['folio'].isin(n7['folio'])].copy()
    n16 = n15.merge(n7, left_on='folio', right_on='folio', how='inner')
    n10_avg_total_e_value_value = n10['avg_total_e_value'].iloc[0]
    n17 = n16[n16['total_e_value'] > n10_avg_total_e_value_value].copy()
    n18 = pd.DataFrame({'crafts_households_above_avg_count': [n17['folio'].count()]})

    return n18