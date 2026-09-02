import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1.0)].copy()
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = tables['ii_crh'].copy()
    n8 = tables['ii_crh'].copy()
    n9 = n7.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9[n9['folio'].isin(n6['folio'])].copy()
    n11 = n10[(n10['crh03_1_x'] == 1.0) & (n10['crh04_1_y'] == 1.0)].copy()
    n12 = pd.DataFrame({'avg_total_debt': [n11['crh04_2_y'].mean()]})
    n12_avg_total_debt_value = n12['avg_total_debt'].iloc[0]
    n13 = n11[n11['crh04_2_y'] > n12_avg_total_debt_value].copy()
    n14 = n13[['folio', 'crh04_2_y', 'crh03_1_x', 'crh04_1_y']].copy()
    n15 = n14.sort_values('crh04_2_y', ascending=False)

    return n15