import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_crh'].copy()
    n3 = n1.merge(n1, left_on='folio', right_on='folio', how='inner')
    n4 = n3[(n3['edad_x'] >= 18) & (n3['edad_y'] < 18)].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(adult_child_pairs=('folio', 'count'))
    n6 = n2[(n2['crh02_1'] == 1)].copy()
    n7 = n5[n5['folio'].isin(n6['folio'])].copy()
    n8 = pd.DataFrame({'num_households_adult_child_among_debt': [n7['folio'].count()]})

    return n8