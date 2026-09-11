import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_members_oaxaca=('ls', 'count'))
    n4 = n3[['folio']].copy()
    n5 = tables['ii_su'].copy()
    n6 = n5[(n5['su01'] == 1.0) & (n5['su231'] > 0)].copy()
    n7 = n6[n6['folio'].isin(n4['folio'])].copy()
    n8 = tables['ii_su'].copy()
    n9 = n8[(n8['su01'] == 1.0) & (n8['su231'] > 0)].copy()
    n10 = pd.DataFrame({'avg_fertilizer_expense_land_users': [n9['su231'].mean()]})
    n10_avg_fertilizer_expense_land_users_value = n10['avg_fertilizer_expense_land_users'].iloc[0]
    n11 = n7[n7['su231'] > n10_avg_fertilizer_expense_land_users_value].copy()
    n12 = n11[['folio', 'su231']].copy()
    n13 = n12.sort_values('su231', ascending=False)

    return n13