import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 60.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(n_seniors=('folio', 'count'))
    n5 = tables['ii_vlh'].copy()
    n6 = n5[(n5['vlh04'].isin([3.0, 4.0]))].copy()
    n7 = n4.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_se'].copy()
    n9 = n8[(n8['se01a'] == 1.0)].copy()
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = pd.DataFrame({'n_households': [n10['folio'].count()]})

    return n11