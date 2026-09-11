import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_adults=('ls', 'count'))
    n4 = tables['ii_ah'].copy()
    n5 = n4[(n4['ah03g'] == 1)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(n_owners=('ls', 'count'))
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_se'].copy()
    n9 = n8[(n8['se01a'] == 1)].copy()
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n12 = n9.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = n12.groupby(['ent'], as_index=False).agg(denominator_households=('folio', 'count'))
    n14 = n10.merge(n11, left_on='folio', right_on='folio', how='inner')
    n15 = n14.groupby(['ent'], as_index=False).agg(numerator_households=('folio', 'count'))
    n16 = n15.merge(n13, left_on='ent', right_on='ent', how='inner')
    n17 = n16[['ent', 'numerator_households', 'denominator_households']].copy()

    return n17