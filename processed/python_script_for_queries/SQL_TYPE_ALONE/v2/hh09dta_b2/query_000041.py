import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[['folio', 'ent']].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n4 = tables['ii_vlh'].copy()
    n5 = n4.merge(n3, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_ah'].copy()
    n7 = n6[(n6['ah03g'] == 1.0)].copy()
    n8 = n7[['folio']].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(n_members_with_appliance=('folio', 'count'))
    n10 = n5[n5['folio'].isin(n9['folio'])].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'), no_since2005=('vlh12a_c', 'count'), yes_current=('vlh12a_a', 'count'))
    n12 = n11[(n11['n_households'] >= 25) & (n11['no_since2005'] > 0) & (n11['no_since2005'] > {'column': 'yes_current'})].copy()

    return n12