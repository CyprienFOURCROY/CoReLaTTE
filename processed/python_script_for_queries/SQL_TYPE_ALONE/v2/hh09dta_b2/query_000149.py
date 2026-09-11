import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18) & (n1['ent'] == 20)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = n4[['folio', 'ent', 'edad', 'ah03d', 'ls_x', 'ls_y']].copy()
    n6 = tables['ii_in'].copy()
    n7 = n6[(n6['in03a'] == 1)].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8[(n8['ah03d'].isin([1, 3]))].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(min_ah03d=('ah03d', 'min'))
    n11 = n10.groupby(['min_ah03d'], as_index=False).agg(households=('folio', 'count'))

    return n11