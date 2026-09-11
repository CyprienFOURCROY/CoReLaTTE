import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1.0)].copy()
    n3 = pd.DataFrame({'avg_workers_expense': [n2['su237'].mean()]})
    n4 = tables['ii_crh'].copy()
    n5 = n4[(n4['crh01_1b'] == 2.0)].copy()
    n6 = n2.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6[(n6['su237'] > 0.0)].copy()
    n3_avg_workers_expense_value = n3['avg_workers_expense'].iloc[0]
    n8 = n7[n7['su237'] > n3_avg_workers_expense_value].copy()
    n9 = n8[['folio', 'su237']].copy()
    n10 = n9.sort_values('su237', ascending=False)

    return n10