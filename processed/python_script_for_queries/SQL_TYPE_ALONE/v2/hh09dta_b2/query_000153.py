import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 60)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(senior_count=('folio', 'count'))
    n4 = tables['ii_crh'].copy()
    n5 = n4[(n4['crh04_1'] == 1) & (n4['crh04_2'] > 0)].copy()
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = n6.merge(n3, left_on='folio', right_on='folio', how='inner')
    n8 = pd.DataFrame({'avg_debt': [n7['crh04_2'].mean()]})
    n8_avg_debt_value = n8['avg_debt'].iloc[0]
    n9 = n7[n7['crh04_2'] > n8_avg_debt_value].copy()
    n10 = tables['ii_in'].copy()
    n11 = n9.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11[(n11['in01a10_1'] == 1)].copy()
    n13 = pd.DataFrame({'avg_in02a10': [n12['in02a10'].mean()]})

    return n13