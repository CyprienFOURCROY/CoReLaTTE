import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.merge(n1, left_on='ent', right_on='ent', how='inner')
    n3 = n2[(n2['edad_x'] < 30) & (n2['edad_y'] >= 50)].copy()
    n4 = n3[['folio_x', 'ent_x']].copy()
    n5 = n4.groupby(['folio_x', 'ent_x'], as_index=False).agg(pair_count=('folio_x', 'count'))
    n6 = tables['ii_vlh'].copy()
    n7 = n5.merge(n6, left_on='folio_x', right_on='folio', how='inner')
    n8 = n7[(n7['vlh18a'] == 0)].copy()
    n9 = tables['ii_nna'].copy()
    n10 = n9[(n9['nna01'] == 1)].copy()
    n11 = n8.merge(n10, left_on='folio_x', right_on='folio', how='inner')
    n12 = n11.groupby(['ent_x'], as_index=False).agg(n_households=('folio_x', 'count'))
    n13 = n12.sort_values('n_households', ascending=False)

    return n13