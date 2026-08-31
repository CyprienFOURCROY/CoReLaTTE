import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 25.0)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n3[(n3['ah03d'] == 1.0)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = n5.merge(n4, left_on='folio', right_on='folio', how='inner')
    n7 = n6.groupby(['folio', 'ls_x'], as_index=False).agg(edad=('edad', 'max'), ent=('ent', 'max'))
    n8 = tables['ii_crh'].copy()
    n9 = n8[(n8['crh03_1'] == 1.0) & (n8['crh03_2'] > 0.0)].copy()
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10.groupby(['folio'], as_index=False).agg(hh_paid=('crh03_2', 'max'))
    n12 = pd.DataFrame({'overall_avg_paid': [n11['hh_paid'].mean()]})
    n12_overall_avg_paid_value = n12['overall_avg_paid'].iloc[0]
    n13 = n10[n10['crh03_2'] > n12_overall_avg_paid_value].copy()
    n14 = pd.DataFrame({'avg_age_above_overall': [n13['edad'].mean()]})

    return n14