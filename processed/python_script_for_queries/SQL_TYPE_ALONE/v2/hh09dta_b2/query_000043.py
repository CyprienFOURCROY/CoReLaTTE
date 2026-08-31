import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh12a_c'] == 3.0)].copy()
    n3 = tables['ii_portad'].copy()
    n4 = n3[(n3['edad'] >= 18.0)].copy()
    n5 = n4.merge(n2, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_ah'].copy()
    n7 = n6[(n6['ah03d1'] == 1.0)].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(car_yes_count=('ah03d1', 'count'))
    n9 = n5.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['ent'], as_index=False).agg(adult_count=('folio', 'count'))
    n11 = pd.DataFrame({'avg_adult_count': [n10['adult_count'].mean()]})
    n11_avg_adult_count_value = n11['avg_adult_count'].iloc[0]
    n12 = n10[n10['adult_count'] > n11_avg_adult_count_value].copy()
    n13 = n12.sort_values('adult_count', ascending=False)
    n14 = n13[['ent', 'adult_count']].copy()

    return n14