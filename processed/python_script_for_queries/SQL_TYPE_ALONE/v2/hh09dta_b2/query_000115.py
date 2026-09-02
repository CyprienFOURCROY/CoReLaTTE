import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n4 = n3[['folio']].copy()
    n5 = tables['ii_ah'].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(vehicle_value_sum=('ah04d_2', 'sum'), vehicle_value_flag=('ah04d_1', 'max'))
    n7 = n6[n6['folio'].isin(n4['folio'])].copy()
    n8 = tables['ii_se'].copy()
    n9 = n8[(n8['se01b'] == 1.0)].copy()
    n10 = n9[['folio', 'se01b']].copy()
    n11 = n7.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11[(n11['vehicle_value_flag'] == 1.0)].copy()
    n13 = pd.DataFrame({'avg_vehicle_value': [n12['vehicle_value_sum'].mean()]})
    n13_avg_vehicle_value_value = n13['avg_vehicle_value'].iloc[0]
    n14 = n12[n12['vehicle_value_sum'] < n13_avg_vehicle_value_value].copy()
    n15 = tables['ii_crh'].copy()
    n16 = n15[(n15['crh04_1'] == 1.0)].copy()
    n17 = n16[['folio', 'crh04_2']].copy()
    n18 = n14.merge(n17, left_on='folio', right_on='folio', how='inner')
    n19 = pd.DataFrame({'avg_debts_below_avg_vehicle': [n18['crh04_2'].mean()]})

    return n19