import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio', 'ent'], as_index=False).agg(n_persons=('ls', 'count'))
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 3.0)].copy()
    n5 = tables['ii_nna'].copy()
    n6 = n5[(n5['nna01'] == 1.0)].copy()
    n7 = n6[n6['folio'].isin(n4['folio'])].copy()
    n8 = n7.merge(n2, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(avg_businesses=('nna02', 'mean'), n_households=('folio', 'count'))
    n10 = n9[(n9['avg_businesses'] >= 1.5)].copy()
    n11 = n10.sort_values('avg_businesses', ascending=False)
    n12 = n11[['ent', 'avg_businesses', 'n_households']].copy()

    return n12