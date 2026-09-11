import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh02_1'] == 1.0)].copy()
    n3 = tables['ii_crh'].copy()
    n4 = n3[(n3['crh03_1'] == 1.0)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[(n5['crh03_2_y'] > {'column_ref': 'crh02_2_x'})].copy()
    n7 = pd.DataFrame({'mean_crh02_2': [n2['crh02_2'].mean()]})
    n7_mean_crh02_2_value = n7['mean_crh02_2'].iloc[0]
    n8 = n6[n6['crh03_2_y'] > n7_mean_crh02_2_value].copy()
    n9 = tables['ii_nna'].copy()
    n10 = n9[(n9['nna01'] == 1.0)].copy()
    n11 = n8[n8['folio'].isin(n10['folio'])].copy()
    n12 = n11[['folio']].copy()
    n13 = n12.groupby(['folio'], as_index=False).agg(hh_rows=('folio', 'count'))
    n14 = tables['ii_portad'].copy()
    n15 = n14[['folio', 'ent']].copy()
    n16 = n15.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n17 = n13.merge(n16, left_on='folio', right_on='folio', how='inner')
    n18 = n17.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n19 = n18.sort_values('n_households', ascending=False)

    return n19