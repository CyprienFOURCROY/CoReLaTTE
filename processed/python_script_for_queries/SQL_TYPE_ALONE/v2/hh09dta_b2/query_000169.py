import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2[['folio', 'ls', 'edad']].copy()
    n4 = n2[['folio', 'ls', 'edad']].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[(n5['edad_x'] >= 60.0) & (n5['edad_y'] < 30.0)].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(pair_count=('edad_x', 'count'))
    n8 = tables['ii_crh'].copy()
    n9 = n8[(n8['crh04_1'] == 1.0) & (n8['crh04_2'] > 0.0)].copy()
    n10 = n9[['folio', 'crh04_2']].copy()
    n11 = n10.merge(n7, left_on='folio', right_on='folio', how='inner')
    n12 = n2.groupby(['folio'], as_index=False).agg(hhm_count=('ls', 'count'))
    n13 = n10.merge(n12, left_on='folio', right_on='folio', how='inner')
    n14 = pd.DataFrame({'oax_avg_debt': [n13['crh04_2'].mean()]})
    n14_oax_avg_debt_value = n14['oax_avg_debt'].iloc[0]
    n15 = n11[n11['crh04_2'] >= n14_oax_avg_debt_value].copy()
    n16 = pd.DataFrame({'avg_total_debt_gap_oax_ge_avg': [n15['crh04_2'].mean()]})

    return n16