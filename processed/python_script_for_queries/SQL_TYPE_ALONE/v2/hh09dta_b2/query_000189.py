import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = n4[(n4['ls_y'] == 2.0) & (n4['inr02a'] == 1.0)].copy()
    n6 = n5[['folio', 'ent', 'inr03a']].copy()
    n7 = n6.groupby(['folio', 'ent'], as_index=False).agg(hh_inr03a=('inr03a', 'max'))
    n8 = n7.groupby(['ent'], as_index=False).agg(state_mean_inr03a=('hh_inr03a', 'mean'))
    n9 = pd.DataFrame({'national_mean_inr03a': [n7['hh_inr03a'].mean()]})
    n9_national_mean_inr03a_value = n9['national_mean_inr03a'].iloc[0]
    n10 = n8[n8['state_mean_inr03a'] > n9_national_mean_inr03a_value].copy()
    n11 = n10.sort_values('state_mean_inr03a', ascending=False)
    n12 = n11[['ent', 'state_mean_inr03a']].copy()

    return n12