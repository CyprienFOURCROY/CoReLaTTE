import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_nna'].copy()
    n3 = tables['ii_su'].copy()
    n4 = n2[(n2['nna01'] == 1.0)].copy()
    n5 = n3[(n3['su01'] == 1.0)].copy()
    n6 = n1.merge(n1, left_on='folio', right_on='folio', how='inner')
    n7 = n6[(n6['edad_x'] >= 18.0) & (n6['edad_y'] < 18.0)].copy()
    n8 = n7[['folio', 'ent_x']].copy()
    n9 = n8.merge(n4, left_on='folio', right_on='folio', how='inner')
    n10 = n9.merge(n5, left_on='folio', right_on='folio', how='inner')
    n11 = n10.groupby(['folio'], as_index=False).agg(ent_state=('ent_x', 'min'))
    n12 = n11[(n11['ent_state'] == 20.0)].copy()
    n13 = pd.DataFrame({'household_count': [n12['folio'].count()]})

    return n13