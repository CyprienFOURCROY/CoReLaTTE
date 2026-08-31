import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_adults=('ls', 'count'))
    n4 = tables['ii_ah'].copy()
    n5 = n4[(n4['ah03a'] == 1)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(n_owner_reports=('ls', 'count'))
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['n_adults'] >= 1) & (n7['n_owner_reports'] >= 1)].copy()
    n9 = tables['ii_vlh'].copy()
    n10 = n9[(n9['vlh04'].isin([3, 4])) & (n9['vlh01k'].isin([1, 2]))].copy()
    n11 = n8.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = pd.DataFrame({'n_households': [n11['folio'].count()]})

    return n12