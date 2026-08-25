import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_in'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = tables['ii_vlh'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n7 = n6.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'))
    n7_avg_age_value = n7['avg_age'].iloc[0]
    n8 = n6[n6['edad'] > n7_avg_age_value].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(older_adult_count=('ls', 'count'))
    n10 = n5.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10[(n10['in02a10'] > 0.0)].copy()
    n12 = n11.groupby(['ent', 'folio'], as_index=False).agg(hh_vlh04=('vlh04', 'mean'), hh_in02a10=('in02a10', 'sum'))
    n13 = n12.groupby(['ent'], as_index=False).agg(avg_vlh04_recipients=('hh_vlh04', 'mean'), avg_in02a10=('hh_in02a10', 'mean'), households_count=('folio', 'count'))

    return n13