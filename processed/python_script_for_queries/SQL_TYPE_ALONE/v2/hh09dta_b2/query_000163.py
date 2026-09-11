import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='left')
    n5 = n4[['folio', 'ent', 'edad', 'ah03d']].copy()
    n6 = tables['ii_crh'].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_portad'].copy()
    n9 = n8[(n8['ent'] == 20.0)].copy()
    n10 = n9[['folio']].copy()
    n11 = tables['ii_crh'].copy()
    n12 = n11[(n11['crh04_1'] == 1.0)].copy()
    n13 = n12[n12['folio'].isin(n10['folio'])].copy()
    n14 = pd.DataFrame({'oax_mean_debt': [n13['crh04_2'].mean()]})
    n15 = n7[(n7['ah03d'] == 1.0) & (n7['crh04_1'] == 1.0)].copy()
    n14_oax_mean_debt_value = n14['oax_mean_debt'].iloc[0]
    n16 = n15[n15['crh04_2'] > n14_oax_mean_debt_value].copy()
    n17 = pd.DataFrame({'n_individuals': [n16['folio'].count()]})

    return n17