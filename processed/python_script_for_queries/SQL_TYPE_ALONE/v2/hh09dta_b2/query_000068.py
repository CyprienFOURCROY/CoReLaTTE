import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1.0)].copy()
    n6 = n3.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = tables['ii_se'].copy()
    n8 = n7[(n7['se01a'] == 1.0)].copy()
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['folio'], as_index=False).agg(n_rows_per_household=('folio', 'count'))
    n11 = pd.DataFrame({'n_households': [n10['folio'].count()]})

    return n11