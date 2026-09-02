import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 3)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_crh'].copy()
    n5 = n4[(n4['crh01_1a'] == 1)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_portad'].copy()
    n9 = n8[['folio', 'ent']].copy()
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10.groupby(['ent', 'folio'], as_index=False).agg(rows_per_hh=('folio', 'count'))
    n12 = n11.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n13 = n12[(n12['n_households'] >= 50)].copy()
    n14 = n13.sort_values('n_households', ascending=False)
    n15 = n14[['ent', 'n_households']].copy()

    return n15