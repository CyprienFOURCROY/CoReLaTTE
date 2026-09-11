import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 60.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(senior_count=('edad', 'count'), state=('ent', 'min'))
    n4 = n3[(n3['senior_count'] >= 1)].copy()
    n5 = tables['ii_crh'].copy()
    n6 = n5[(n5['crh04_1'] == 1.0)].copy()
    n7 = n4.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_vlh'].copy()
    n9 = n8[(n8['vlh04'].isin([3.0, 4.0]))].copy()
    n10 = n7.merge(n9, left_on='folio_x', right_on='folio', how='inner')
    n11 = n10.groupby(['state'], as_index=False).agg(avg_debt=('crh04_2', 'mean'))
    n12 = pd.DataFrame({'overall_avg_debt': [n10['crh04_2'].mean()]})
    n12_overall_avg_debt_value = n12['overall_avg_debt'].iloc[0]
    n13 = n11[n11['avg_debt'] >= n12_overall_avg_debt_value].copy()
    n14 = n13.sort_values('avg_debt', ascending=False)
    n15 = n14.head(1)
    n16 = n15[['state', 'avg_debt']].copy()

    return n16