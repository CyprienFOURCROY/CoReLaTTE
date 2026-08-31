import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1)].copy()
    n3 = n2[(n2['su234'] > 0)].copy()
    n4 = pd.DataFrame({'avg_seed_expense_pos_farm': [n3['su234'].mean()]})
    n5 = tables['ii_ah'].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(min_ah03d=('ah03d', 'min'))
    n7 = n6[(n6['min_ah03d'] == 1)].copy()
    n8 = n2[n2['folio'].isin(n7['folio'])].copy()
    n9 = n8[(n8['su234'] > 0)].copy()
    n4_avg_seed_expense_pos_farm_value = n4['avg_seed_expense_pos_farm'].iloc[0]
    n10 = n9[n9['su234'] < n4_avg_seed_expense_pos_farm_value].copy()
    n11 = n10[['folio', 'su234']].copy()

    return n11