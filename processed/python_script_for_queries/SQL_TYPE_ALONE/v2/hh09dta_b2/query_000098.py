import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03d'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_vehicle_owners=('ls', 'count'))
    n4 = n3[(n3['n_vehicle_owners'] >= 1)].copy()
    n5 = tables['ii_portad'].copy()
    n6 = n5[(n5['ent'].isin([20.0, 21.0])) & (n5['edad'] >= 18.0)].copy()
    n7 = n6.groupby(['folio', 'ent'], as_index=False).agg(n_adults=('ls', 'count'))
    n8 = n7[(n7['n_adults'] >= 1)].copy()
    n9 = tables['ii_su'].copy()
    n10 = n9[(n9['su01'] == 1.0)].copy()
    n11 = n5.groupby(['folio', 'ent'], as_index=False).agg(hh_n=('ls', 'count'))
    n12 = n10.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = n12[(n12['ent'].isin([20.0, 21.0]))].copy()
    n14 = pd.DataFrame({'overall_avg_su239': [n13['su239'].mean()]})
    n16 = n10.merge(n8, left_on='folio', right_on='folio', how='inner')
    n17 = n16.merge(n4, left_on='folio', right_on='folio', how='inner')
    n14_overall_avg_su239_value = n14['overall_avg_su239'].iloc[0]
    n18 = n17[n17['su239'] > n14_overall_avg_su239_value].copy()
    n19 = pd.DataFrame({'n_households': [n18['folio'].count()]})

    return n19