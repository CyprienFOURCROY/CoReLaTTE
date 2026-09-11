import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3[(n3['edad_x'] >= 60) & (n3['edad_y'] < 30)].copy()
    n5 = n4[['folio_x']].copy()
    n6 = n5.groupby(['folio_x'], as_index=False).agg(qualifying_pairs=('folio_x', 'count'))
    n7 = tables['ii_nna'].copy()
    n8 = n6.merge(n7, left_on='folio_x', right_on='folio', how='inner')
    n9 = n8.groupby(['nna01'], as_index=False).agg(households_count=('folio_x', 'count'))

    return n9