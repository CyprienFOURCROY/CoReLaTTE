import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh04'].isin([1, 2]))].copy()
    n3 = tables['ii_portad'].copy()
    n4 = n3[(n3['ent'] == 20) & (n3['edad'] >= 18)].copy()
    n5 = n4.merge(n2, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_ah'].copy()
    n7 = n6[(n6['ah03d'] == 1)].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(mv_count=('ah03d', 'count'))
    n9 = n5.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = pd.DataFrame({'subset_avg_age': [n9['edad'].mean()], 'subset_total': [n9['edad'].count()]})
    n10_subset_avg_age_value = n10['subset_avg_age'].iloc[0]
    n11 = n9[n9['edad'] > n10_subset_avg_age_value].copy()
    n12 = n1[(n1['vlh12a_c'] != 3)].copy()
    n13 = n11[n11['folio'].isin(n12['folio'])].copy()
    n14 = pd.DataFrame({'older_than_avg_count': [n13['edad'].count()]})

    return n14