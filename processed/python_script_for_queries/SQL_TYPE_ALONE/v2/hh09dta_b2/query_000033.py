import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_selected_individuals=('ls', 'count'))
    n4 = tables['ii_ah'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(hh_ah03e_min=('ah03e', 'min'))
    n6 = tables['ii_se'].copy()
    n7 = n6[(n6['se01a'] == 1.0)].copy()
    n8 = tables['ii_vlh'].copy()
    n9 = n8.merge(n5, left_on='folio', right_on='folio', how='inner')
    n10 = n9.merge(n7, left_on='folio', right_on='folio', how='inner')
    n11 = n10[n10['folio'].isin(n3['folio'])].copy()
    n12 = n11[['folio', 'hh_ah03e_min', 'vlh18a']].copy()
    n13 = n12[(n12['hh_ah03e_min'].isin([1.0, 3.0]))].copy()
    n14 = n13.groupby(['hh_ah03e_min'], as_index=False).agg(avg_vlh18a=('vlh18a', 'mean'), n_households=('folio', 'count'))
    n15 = pd.DataFrame({'overall_mean_vlh18a': [n13['vlh18a'].mean()]})
    n15_overall_mean_vlh18a_value = n15['overall_mean_vlh18a'].iloc[0]
    n16 = n14[n14['avg_vlh18a'] >= n15_overall_mean_vlh18a_value].copy()

    return n16