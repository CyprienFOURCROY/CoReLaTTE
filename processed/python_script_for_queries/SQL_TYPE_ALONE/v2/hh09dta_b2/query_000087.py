import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 65)].copy()
    n3 = tables['ii_crh'].copy()
    n4 = n3[(n3['crh04_1'] == 1) & (n3['crh04_2'] >= 0)].copy()
    n5 = n4[n4['folio'].isin(n2['folio'])].copy()
    n6 = pd.DataFrame({'avg_debt_elderly': [n5['crh04_2'].mean()]})
    n6_avg_debt_elderly_value = n6['avg_debt_elderly'].iloc[0]
    n7 = n5[n5['crh04_2'] > n6_avg_debt_elderly_value].copy()
    n8 = tables['ii_in'].copy()
    n9 = n8[(n8['in02a10'] > 0)].copy()
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10[['folio', 'crh04_2', 'in02a10']].copy()
    n12 = n11.sort_values('crh04_2', ascending=False)

    return n12