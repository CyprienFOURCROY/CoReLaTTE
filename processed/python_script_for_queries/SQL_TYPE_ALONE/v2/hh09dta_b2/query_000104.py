import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2[(n2['edad'] >= 18.0)].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(n_adults=('ls', 'count'))
    n5 = n4[(n4['n_adults'] >= 1)].copy()
    n6 = tables['ii_nna'].copy()
    n7 = n6[(n6['nna01'] == 1.0)].copy()
    n8 = n7[n7['folio'].isin(n5['folio'])].copy()
    n9 = tables['ii_crh'].copy()
    n10 = n9[(n9['crh02_1'] == 1.0)].copy()
    n11 = n9[(n9['crh03_1'] == 1.0)].copy()
    n12 = n10.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = n12[n12['folio'].isin(n8['folio'])].copy()
    n14 = pd.DataFrame({'avg_paid': [n13['crh03_2_y'].mean()]})
    n14_avg_paid_value = n14['avg_paid'].iloc[0]
    n15 = n13[n13['crh03_2_y'] > n14_avg_paid_value].copy()
    n16 = n15[['folio', 'crh02_2_x', 'crh03_2_y']].copy()
    n17 = n16.sort_values('crh03_2_y', ascending=False)

    return n17