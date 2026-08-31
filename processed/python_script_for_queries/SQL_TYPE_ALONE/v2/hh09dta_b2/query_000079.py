import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 60.0)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n3[(n3['ah04h_1'] == 1.0) & (n3['ah04h_2'] > 0.0)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[(n5['ls_y'] >= 1.0)].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(hh_has_elderly_fin_assets=('edad', 'count'))
    n8 = tables['ii_crh'].copy()
    n9 = n8[(n8['crh04_1'] == 1.0)].copy()
    n10a = pd.DataFrame({'avg_crh04_2': [n9['crh04_2'].mean()]})
    n10a_avg_crh04_2_value = n10a['avg_crh04_2'].iloc[0]
    n10 = n9[n9['crh04_2'] > n10a_avg_crh04_2_value].copy()
    n11 = n7[n7['folio'].isin(n10['folio'])].copy()
    n12 = tables['ii_in'].copy()
    n13 = n12[(n12['in02a10'] > 0.0)].copy()
    n14 = n11[n11['folio'].isin(n13['folio'])].copy()
    n15 = tables['ii_portad'].copy()
    n16 = n15.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n17 = n11.merge(n16, left_on='folio', right_on='folio', how='inner')
    n18 = n17.groupby(['ent'], as_index=False).agg(denom_households=('folio', 'count'))
    n19 = n14.merge(n16, left_on='folio', right_on='folio', how='inner')
    n20 = n19.groupby(['ent'], as_index=False).agg(numer_households=('folio', 'count'))
    n21 = n18.merge(n20, left_on='ent', right_on='ent', how='left')
    n22 = n21.sort_values('numer_households', ascending=False)
    n23 = n22[['ent', 'denom_households', 'numer_households']].copy()

    return n23