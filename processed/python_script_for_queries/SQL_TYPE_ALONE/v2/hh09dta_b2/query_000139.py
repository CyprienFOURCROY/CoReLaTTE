import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_portad'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3[(n3['edad_x'] >= 70) & (n3['edad_y'] < 12)].copy()
    n5 = n4.groupby(['folio', 'ent_x'], as_index=False).agg(n_pairs=('ls_x', 'count'))
    n6 = tables['ii_in'].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['in03a'] == 1)].copy()
    n9 = n8.groupby(['ent_x'], as_index=False).agg(hh_with_liconsa=('folio', 'count'))
    n10 = pd.DataFrame({'national_mean_hh_with_liconsa': [n9['hh_with_liconsa'].mean()]})
    n10_national_mean_hh_with_liconsa_value = n10['national_mean_hh_with_liconsa'].iloc[0]
    n11 = n9[n9['hh_with_liconsa'] > n10_national_mean_hh_with_liconsa_value].copy()
    n12 = n11.sort_values('hh_with_liconsa', ascending=False)
    n13 = n12[['ent_x', 'hh_with_liconsa']].copy()

    return n13