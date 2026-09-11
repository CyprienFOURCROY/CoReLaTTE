import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_individuals_oax=('ls', 'count'))
    n4 = tables['ii_ah'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(any_motor_vehicle_flag=('ah03d', 'min'), motor_vehicle_value=('ah04d_2', 'max'))
    n6 = n5[(n5['any_motor_vehicle_flag'] == 1.0)].copy()
    n7 = n6[n6['folio'].isin(n3['folio'])].copy()
    n8 = tables['ii_crh'].copy()
    n9 = n8[(n8['crh04_1'] == 1.0)].copy()
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = pd.DataFrame({'avg_motor_vehicle_value_oaxaca_households_with_debt': [n10['motor_vehicle_value'].mean()]})

    return n11