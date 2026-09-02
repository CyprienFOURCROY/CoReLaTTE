import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_crh'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = n5[(n5['crh04_1'] == 1.0)].copy()
    n7 = pd.DataFrame({'mean_debt_total': [n6['crh04_2'].mean()]})
    n7_mean_debt_total_value = n7['mean_debt_total'].iloc[0]
    n8 = n6[n6['crh04_2'] > n7_mean_debt_total_value].copy()
    n9 = tables['ii_in'].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(sum_in02a10=('in02a10', 'sum'))
    n11 = n10[(n10['sum_in02a10'] > 0.0)].copy()
    n12 = n11[n11['folio'].isin(n8['folio'])].copy()
    n13 = pd.DataFrame({'num_households': [n12['folio'].count()]})

    return n13