import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 25.0) & (n1['edad'] <= 54.0)].copy()
    n3 = n2[['folio', 'ent', 'edad', 'ls']].copy()
    n4 = tables['ii_ah'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[['folio', 'ent', 'edad', 'ah03h', 'ls_x', 'ls_y']].copy()
    n7 = n6[(n6['ah03h'] == 1.0)].copy()
    n8 = n2.groupby(['folio'], as_index=False).agg(n_individuals=('ls', 'count'))
    n9 = n8[['folio']].copy()
    n10 = tables['ii_crh'].copy()
    n11 = n10[(n10['crh04_1'] == 1.0)].copy()
    n12 = n11[n11['folio'].isin(n9['folio'])].copy()
    n13 = pd.DataFrame({'mean_debt': [n12['crh04_2'].mean()]})
    n14 = n7.groupby(['folio'], as_index=False).agg(n_assets_members=('ah03h', 'count'))
    n15 = n14[['folio']].copy()
    n16 = n12[n12['folio'].isin(n15['folio'])].copy()
    n13_mean_debt_value = n13['mean_debt'].iloc[0]
    n17 = n16[n16['crh04_2'] > n13_mean_debt_value].copy()
    n18 = n17.groupby(['folio'], as_index=False).agg(rows_per_folio=('crh04_2', 'count'))
    n19 = pd.DataFrame({'num_households': [n18['folio'].count()]})

    return n19