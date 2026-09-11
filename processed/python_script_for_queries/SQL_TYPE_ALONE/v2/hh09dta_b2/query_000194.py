import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_ah'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3.groupby(['ent', 'folio', 'ls_x', 'edad'], as_index=False).agg(min_ah03e=('ah03e', 'min'))
    n5 = n4[(n4['min_ah03e'] == 1.0)].copy()
    n6 = n5.groupby(['ent'], as_index=False).agg(total_individuals_in_device_households=('ls_x', 'count'))
    n7 = n5[(n5['edad'] >= 18.0) & (n5['edad'] <= 24.0)].copy()
    n8 = n7.groupby(['ent'], as_index=False).agg(age18_24_count=('ls_x', 'count'))
    n9 = n8.merge(n6, left_on='ent', right_on='ent', how='inner')
    n10 = pd.DataFrame({'avg_age18_24_count': [n8['age18_24_count'].mean()]})
    n10_avg_age18_24_count_value = n10['avg_age18_24_count'].iloc[0]
    n11 = n9[n9['age18_24_count'] > n10_avg_age18_24_count_value].copy()
    n12 = n11.sort_values('age18_24_count', ascending=False)
    n13 = n12[['ent', 'age18_24_count', 'total_individuals_in_device_households']].copy()

    return n13