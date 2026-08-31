import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = tables['ii_crh'].copy()
    n4 = n3[(n3['crh04_1'] == 1)].copy()
    n5 = pd.DataFrame({'avg_total_debts': [n4['crh04_2'].mean()]})
    n6 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n5_avg_total_debts_value = n5['avg_total_debts'].iloc[0]
    n7 = n6[n6['crh04_2'] > n5_avg_total_debts_value].copy()
    n8 = n7.groupby(['ent'], as_index=False).agg(adult_count_above_avg_debt=('ls', 'count'))
    n9 = n8.sort_values('adult_count_above_avg_debt', ascending=False)
    n10 = n9.head(10)

    return n10