import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_inr'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3[(n3['inr02d'] == 1.0) & (n3['ls_y'] >= 1.0)].copy()
    n5 = n4.groupby(['folio', 'ent'], as_index=False).agg(max_age=('edad', 'max'))
    n6 = pd.DataFrame({'avg_max_age_egg_hh': [n5['max_age'].mean()]})
    n7 = tables['ii_ah'].copy()
    n8 = n7[(n7['ah03m'] == 1.0)].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(n_poultry_members=('ls', 'count'))
    n10 = n5[(n5['ent'] == 20.0)].copy()
    n11 = n10[n10['folio'].isin(n9['folio'])].copy()
    n6_avg_max_age_egg_hh_value = n6['avg_max_age_egg_hh'].iloc[0]
    n12 = n11[n11['max_age'] >= n6_avg_max_age_egg_hh_value].copy()
    n13 = pd.DataFrame({'n_households': [n12['folio'].count()]})
    n14 = n13[['n_households']].copy()

    return n14