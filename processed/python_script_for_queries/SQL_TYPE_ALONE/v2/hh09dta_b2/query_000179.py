import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = n2[['folio', 'ls', 'edad']].copy()
    n4 = tables['ii_ah'].copy()
    n5 = n4[['folio', 'ls', 'ah03m']].copy()
    n6 = n3.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6.groupby(['folio', 'ls_x', 'edad'], as_index=False).agg(hh_any_poultry=('ah03m', 'min'))
    n8 = tables['ii_vlh'].copy()
    n9 = n8[(n8['vlh12a_a'] == 1.0)].copy()
    n10 = n9[['folio']].copy()
    n11 = n7[n7['folio'].isin(n10['folio'])].copy()
    n12 = pd.DataFrame({'overall_mean_age': [n11['edad'].mean()]})
    n12_overall_mean_age_value = n12['overall_mean_age'].iloc[0]
    n13 = n11[n11['edad'] > n12_overall_mean_age_value].copy()
    n14 = n13.groupby(['hh_any_poultry'], as_index=False).agg(mean_age=('edad', 'mean'), n_adults=('edad', 'count'))

    return n14