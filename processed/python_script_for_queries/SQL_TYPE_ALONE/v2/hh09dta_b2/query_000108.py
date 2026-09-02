import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 60.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_qualifying_members=('ls', 'count'))
    n4 = n3[['folio']].copy()
    n5 = tables['ii_vlh'].copy()
    n6 = n5[(n5['vlh04'].isin([3.0, 4.0]))].copy()
    n7 = n6[['folio']].copy()
    n8 = n4[n4['folio'].isin(n7['folio'])].copy()
    n9 = n8.merge(n5, left_on='folio', right_on='folio', how='inner')
    n10 = tables['ii_crh'].copy()
    n11 = n10[(n10['crh02_1'] == 2.0)].copy()
    n12 = n11[['folio']].copy()
    n13 = n9[~n9['folio'].isin(n12['folio'])].copy()
    n14 = n10[(n10['crh02_1'] == 1.0)].copy()
    n15 = n14[['folio']].copy()
    n16 = n13[n13['folio'].isin(n15['folio'])].copy()
    n17 = n16.merge(n10, left_on='folio', right_on='folio', how='inner')
    n18 = pd.DataFrame({'n_households_qualifying': [n17['folio'].count()]})

    return n18