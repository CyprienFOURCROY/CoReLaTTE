import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = tables['ii_crh'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = tables['ii_portad'].copy()
    n5 = n4[(n4['edad'] >= 18.0)].copy()
    n6 = n5[(n5['ent'] == 20.0)].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n8 = n3.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n1[(n1['in03a'] == 1.0)].copy()
    n10 = n8[~n8['folio'].isin(n9['folio'])].copy()
    n11 = n10[(n10['crh04_1'] == 1.0) & (n10['crh04_2'] > 0.0)].copy()
    n12 = pd.DataFrame({'avg_debt': [n11['crh04_2'].mean()]})
    n12_avg_debt_value = n12['avg_debt'].iloc[0]
    n13 = n11[n11['crh04_2'] > n12_avg_debt_value].copy()
    n14 = n13[(n13['in02a10'] > 0.0)].copy()
    n15 = pd.DataFrame({'households_count': [n14['folio'].count()]})

    return n15