import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1.0)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(workers_expense=('su237', 'sum'))
    n7 = n6.merge(n3, left_on='folio', right_on='folio', how='inner')
    n8 = pd.DataFrame({'mean_workers_expense': [n7['workers_expense'].mean()]})
    n8_mean_workers_expense_value = n8['mean_workers_expense'].iloc[0]
    n9 = n7[n7['workers_expense'] > n8_mean_workers_expense_value].copy()
    n10 = tables['ii_crh'].copy()
    n11 = n10[(n10['crh04_1'] == 1.0) & (n10['crh04_2'] > 0.0)].copy()
    n12 = n11[['folio', 'crh04_2']].copy()
    n13 = n9.merge(n12, left_on='folio', right_on='folio', how='inner')
    n14 = tables['ii_ah'].copy()
    n15 = n14[['folio', 'ah04e_2']].copy()
    n16 = n15.groupby(['folio'], as_index=False).agg(elec_value=('ah04e_2', 'max'))
    n17 = n13.merge(n16, left_on='folio', right_on='folio', how='inner')
    n18 = pd.DataFrame({'avg_elec_value': [n17['elec_value'].mean()]})

    return n18