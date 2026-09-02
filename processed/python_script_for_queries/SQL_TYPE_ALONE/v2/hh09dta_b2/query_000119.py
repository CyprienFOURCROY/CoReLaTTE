import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = n4[(n4['ls_y'] == 1.0) & (n4['ah03d'] == 1.0)].copy()
    n6 = tables['ii_su'].copy()
    n7 = n6[(n6['su01'] == 1.0)].copy()
    n8 = n7[['folio']].copy()
    n9 = n5.groupby(['folio'], as_index=False).agg(n_qualifying_rows=('folio', 'count'))
    n10 = n9[n9['folio'].isin(n8['folio'])].copy()
    n11 = n10[['folio']].copy()

    return n11