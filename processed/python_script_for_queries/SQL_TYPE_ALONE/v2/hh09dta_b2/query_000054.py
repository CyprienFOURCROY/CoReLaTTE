import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = n4.groupby(['folio', 'ls_x'], as_index=False).agg(has_electronics=('ah03e', 'max'))
    n6 = tables['ii_se'].copy()
    n7 = n6[(n6['se01b'] == 1.0)].copy()
    n8 = n5[n5['folio'].isin(n7['folio'])].copy()
    n9 = n1[(n1['ent'] == 20.0)].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(cnt=('folio', 'count'))
    n11 = tables['ii_crh'].copy()
    n12 = n11[(n11['crh04_1'] == 1.0) & (n11['crh04_2'] > 0.0)].copy()
    n13 = n12[n12['folio'].isin(n10['folio'])].copy()
    n14 = pd.DataFrame({'avg_debt_oax': [n13['crh04_2'].mean()]})
    n15 = n8.merge(n13, left_on='folio', right_on='folio', how='inner')
    n14_avg_debt_oax_value = n14['avg_debt_oax'].iloc[0]
    n16 = n15[n15['crh04_2'] > n14_avg_debt_oax_value].copy()
    n17 = tables['ii_nna'].copy()
    n18 = n17[(n17['nna01'] == 1.0)].copy()
    n19 = n16[n16['folio'].isin(n18['folio'])].copy()
    n20 = n19[(n19['has_electronics'] == 1.0)].copy()
    n21 = pd.DataFrame({'num_individuals_with_electronics': [n20['ls_x'].count()]})

    return n21