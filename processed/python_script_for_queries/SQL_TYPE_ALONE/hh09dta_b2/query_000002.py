import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01a'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_nna'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(avg_businesses=('nna02', 'mean'), num_households=('folio', 'count'))
    n10 = n9.sort_values('avg_businesses', ascending=False)

    return n10