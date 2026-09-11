import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh04_1'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_ah'].copy()
    n5 = n4[(n4['ah03e'] == 1.0)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(n_device_owners=('ls', 'count'))
    n7 = n6[(n6['n_device_owners'] >= 1.0)].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8.groupby(['folio', 'ent'], as_index=False).agg(n_persons_in_household=('ls', 'count'))
    n10 = n3[n3['folio'].isin(n7['folio'])].copy()
    n11 = n10.merge(n9, left_on='folio', right_on='folio', how='inner')
    n12 = n11.groupby(['ent'], as_index=False).agg(n_households_with_debt_and_device=('folio', 'count'))
    n13 = pd.DataFrame({'avg_count_across_states': [n12['n_households_with_debt_and_device'].mean()]})
    n13_avg_count_across_states_value = n13['avg_count_across_states'].iloc[0]
    n14 = n12[n12['n_households_with_debt_and_device'] >= n13_avg_count_across_states_value].copy()

    return n14