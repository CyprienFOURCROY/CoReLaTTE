import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18) & (n1['ent'] == 20)].copy()
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 1)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[['folio', 'ls', 'ent', 'edad', 'su01']].copy()
    n7 = tables['ii_vlh'].copy()
    n8 = n6.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8[['ent', 'ls', 'vlh04']].copy()
    n10 = n9[(n9['vlh04'].isin([1, 2, 3, 4]))].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(n_adults_valid=('ls', 'count'))
    n12 = n10[(n10['vlh04'].isin([3, 4]))].copy()
    n13 = n12.groupby(['ent'], as_index=False).agg(n_adults_unsafe=('ls', 'count'))
    n14 = n11.merge(n13, left_on='ent', right_on='ent', how='left')
    n15 = n14[['ent', 'n_adults_valid', 'n_adults_unsafe']].copy()

    return n15