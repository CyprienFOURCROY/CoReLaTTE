import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(members_count=('ls', 'count'))
    n4 = n3[['folio']].copy()
    n5 = tables['ii_crh'].copy()
    n6 = n5[(n5['crh02_1'] == 1.0) & (n5['crh04_1'] == 1.0)].copy()
    n7 = n6[n6['folio'].isin(n4['folio'])].copy()
    n8 = tables['ii_ah'].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(ah03d_min=('ah03d', 'min'))
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10.groupby(['ah03d_min'], as_index=False).agg(avg_total_debts=('crh04_2', 'mean'), household_count=('folio', 'count'))
    n12 = n11.sort_values('ah03d_min', ascending=True)

    return n12