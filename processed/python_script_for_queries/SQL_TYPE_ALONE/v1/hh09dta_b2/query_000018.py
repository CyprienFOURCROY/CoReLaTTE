import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in02a10'] > 0)].copy()
    n3 = n2[['folio', 'in02a10']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4[['folio', 'ent']].copy()
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n8 = n3.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(avg_in02a10=('in02a10', 'mean'), recipient_hh=('folio', 'count'))
    n10 = n9.sort_values('avg_in02a10', ascending=False)
    n11 = n10.head(1)
    n12 = n9.merge(n11, left_on='avg_in02a10', right_on='avg_in02a10', how='inner')

    return n12