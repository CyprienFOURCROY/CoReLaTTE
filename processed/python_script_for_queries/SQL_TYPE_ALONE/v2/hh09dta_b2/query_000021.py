import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n3 = n2[['folio', 'ent']].copy()
    n4 = tables['ii_vlh'].copy()
    n5 = n4.merge(n3, left_on='folio', right_on='folio', how='left')
    n6 = n5.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n7 = n6[(n6['n_households'] >= 100)].copy()
    n8 = n5[(n5['vlh10a'] == 1.0)].copy()
    n9 = n8.groupby(['ent'], as_index=False).agg(n_known_robbed_12m=('folio', 'count'))
    n10 = n7.merge(n9, left_on='ent', right_on='ent', how='left')
    n11 = n10[['ent', 'n_households', 'n_known_robbed_12m']].copy()
    n12 = n11.sort_values('n_known_robbed_12m', ascending=False)

    return n12