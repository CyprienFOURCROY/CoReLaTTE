import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_ah'].copy()
    n5 = n4[(n4['ah03m'] == 1.0)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(poultry_rows=('ls', 'count'))
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8.groupby(['folio', 'ent'], as_index=False).agg(hh_mean_age=('edad', 'mean'))
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10.groupby(['ent'], as_index=False).agg(state_avg_age=('hh_mean_age', 'mean'), n_households=('folio', 'count'))
    n12 = n11[(n11['n_households'] >= 25)].copy()
    n13 = pd.DataFrame({'global_avg_age': [n10['hh_mean_age'].mean()]})
    n13_global_avg_age_value = n13['global_avg_age'].iloc[0]
    n14 = n12[n12['state_avg_age'] > n13_global_avg_age_value].copy()
    n15 = n14.sort_values('state_avg_age', ascending=False)
    n16 = n15[['ent', 'n_households', 'state_avg_age']].copy()

    return n16