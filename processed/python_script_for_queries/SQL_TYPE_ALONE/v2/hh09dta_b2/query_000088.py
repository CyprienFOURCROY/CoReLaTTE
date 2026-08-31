import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio', 'ent'], as_index=False).agg(adult_count=('ls', 'count'))
    n4 = n3[(n3['ent'] == 20.0) & (n3['adult_count'] >= 1)].copy()
    n5 = tables['ii_crh'].copy()
    n6 = n4.merge(n5, left_on='folio', right_on='folio', how='left')
    n7 = n6[(n6['crh03_1'] == 1.0)].copy()
    n8 = tables['ii_ah'].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(min_ah03g=('ah03g', 'min'), min_ah03d=('ah03d', 'min'))
    n10 = n9[(n9['min_ah03g'] == 1.0) & (n9['min_ah03d'] == 3.0)].copy()
    n11 = n7.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = pd.DataFrame({'avg_paid_12m': [n11['crh03_2'].mean()]})

    return n12