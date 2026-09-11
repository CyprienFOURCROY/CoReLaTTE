import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_adults=('ls', 'count'))
    n4 = tables['ii_in'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='left')
    n6 = tables['ii_su'].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='left')
    n8 = n7[(n7['su01'] == 1.0) & (n7['in01a10_1'] == 1.0) & (n7['in02a10'] > 0.0)].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(n_records=('folio', 'count'))
    n10 = pd.DataFrame({'n_households': [n9['folio'].count()]})

    return n10