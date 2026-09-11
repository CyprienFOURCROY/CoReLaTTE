import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(min_ah03e=('ah03e', 'min'))
    n3 = n2[(n2['min_ah03e'] == 1)].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n6 = n5[(n5['ent'] == 20)].copy()
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_nna'].copy()
    n9 = n7.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9[(n9['nna01'].isin([1, 2]))].copy()
    n11 = n10.groupby(['nna01'], as_index=False).agg(households=('folio', 'count'))

    return n11