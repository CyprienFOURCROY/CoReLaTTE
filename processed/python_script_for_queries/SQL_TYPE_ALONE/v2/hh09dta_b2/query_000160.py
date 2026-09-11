import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_inr'].copy()
    n2 = n1[(n1['inr02a'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(dairy_hh=('folio', 'count'))
    n5 = tables['ii_in'].copy()
    n6 = n5[(n5['in03a'] == 1.0)].copy()
    n7 = n6[['folio']].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(liconsa_hh=('folio', 'count'))
    n9 = tables['ii_portad'].copy()
    n10 = n9[['folio', 'ent']].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n12 = n4.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = n8[n8['folio'].isin(n4['folio'])].copy()
    n14 = n13.merge(n11, left_on='folio', right_on='folio', how='inner')
    n15 = n12.groupby(['ent'], as_index=False).agg(dairy_hh_count=('folio', 'count'))
    n16 = n14.groupby(['ent'], as_index=False).agg(liconsa_and_dairy_hh_count=('folio', 'count'))
    n17 = n15.merge(n16, left_on='ent', right_on='ent', how='left')
    n18 = n17[['ent', 'dairy_hh_count', 'liconsa_and_dairy_hh_count']].copy()

    return n18