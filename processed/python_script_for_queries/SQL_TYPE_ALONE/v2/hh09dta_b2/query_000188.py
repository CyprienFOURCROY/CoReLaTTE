import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[['folio', 'ent', 'edad']].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n4 = n2[(n2['edad'] >= 60)].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(senior_count=('folio', 'count'))
    n6 = n5[(n5['senior_count'] > 0)].copy()
    n7 = tables['ii_se'].copy()
    n8 = n7[(n7['se01a'] == 1.0)].copy()
    n9 = tables['ii_crh'].copy()
    n10 = n9[(n9['crh04_1'] == 1.0)].copy()
    n11 = n8.merge(n3, left_on='folio', right_on='folio', how='inner')
    n12 = n11.merge(n10, left_on='folio', right_on='folio', how='inner')
    n13 = n12[['folio', 'ent']].copy()
    n14 = n13.groupby(['ent'], as_index=False).agg(denominator_hh=('folio', 'count'))
    n15 = n13[n13['folio'].isin(n6['folio'])].copy()
    n16 = n15.groupby(['ent'], as_index=False).agg(numerator_hh=('folio', 'count'))
    n17 = n16.merge(n14, left_on='ent', right_on='ent', how='inner')

    return n17