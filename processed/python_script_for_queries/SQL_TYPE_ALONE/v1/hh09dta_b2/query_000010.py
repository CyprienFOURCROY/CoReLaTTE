import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio', 'ent'], as_index=False).agg(hh_size=('ls', 'count'))
    n4 = tables['ii_nna'].copy()
    n5 = n4[(n4['nna01'] == 1.0)].copy()
    n6 = n3[n3['folio'].isin(n5['folio'])].copy()
    n7 = tables['ii_crh'].copy()
    n8 = n7[(n7['crh04_1'] == 1.0)].copy()
    n9 = n6[n6['folio'].isin(n8['folio'])].copy()
    n10 = n9.merge(n8, left_on='folio', right_on='folio', how='inner')
    n13 = n10[['folio', 'ent', 'hh_size', 'crh04_2']].copy()
    n14 = n13.sort_values('crh04_2', ascending=False)
    n15 = n14.head(10)

    return n15