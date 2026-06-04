import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_nna'].copy()
    n2 = n1[(n1['nna01'] == 1.0)].copy()
    n3 = n2[['folio', 'nna01']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = tables['ii_vlh'].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7.merge(n3, left_on='folio', right_on='folio', how='inner')
    n11 = n8.groupby(['vlh04'], as_index=False).agg(avg_age=('edad', 'mean'), num_individuals=('edad', 'count'))
    n12 = n11.sort_values('avg_age', ascending=False)

    return n12