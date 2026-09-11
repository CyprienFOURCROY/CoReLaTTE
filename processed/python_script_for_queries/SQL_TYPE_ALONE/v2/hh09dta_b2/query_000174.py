import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_portad'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3[(n3['edad_x'] >= 60.0) & (n3['edad_y'] < 15.0)].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(pair_count=('edad_x', 'count'))
    n6 = n5[(n5['pair_count'] > 0.0)].copy()
    n7 = tables['ii_se'].copy()
    n8 = n7[(n7['se01b'] == 1.0)].copy()
    n9 = n6[n6['folio'].isin(n8['folio'])].copy()
    n10 = tables['ii_in'].copy()
    n11 = n9.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11[(n11['in01a10_1'] == 1.0)].copy()
    n13 = pd.DataFrame({'households_count': [n12['folio'].count()]})

    return n13