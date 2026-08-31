import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20)].copy()
    n3 = n2[(n2['edad'] >= 18)].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n5 = tables['ii_nna'].copy()
    n6 = n5[(n5['nna01'] == 1)].copy()
    n7 = n6[n6['folio'].isin(n4['folio'])].copy()
    n8 = n4.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = tables['ii_ah'].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(owner_domestic_min=('ah03g', 'min'))
    n11 = n8.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11[(n11['owner_domestic_min'].isin([1, 3]))].copy()
    n13 = n12.groupby(['owner_domestic_min'], as_index=False).agg(avg_adults=('adult_count', 'mean'), households=('folio', 'count'))
    n14 = n13.sort_values('owner_domestic_min', ascending=True)

    return n14