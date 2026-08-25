import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh04_1'] == 1.0)].copy()
    n3 = pd.DataFrame({'overall_avg_debt': [n2['crh04_2'].mean()]})
    n4 = tables['ii_ah'].copy()
    n5 = n4[(n4['ah03d'] == 1.0)].copy()
    n6 = n2[n2['folio'].isin(n5['folio'])].copy()
    n7 = tables['ii_portad'].copy()
    n8 = n7[(n7['ls'] == '01')].copy()
    n9 = n8[['folio', 'ent']].copy()
    n10 = n6.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10.groupby(['ent'], as_index=False).agg(avg_state_debt=('crh04_2', 'mean'))
    n3_overall_avg_debt_value = n3['overall_avg_debt'].iloc[0]
    n12 = n11[n11['avg_state_debt'] > n3_overall_avg_debt_value].copy()
    n13 = n12.sort_values('avg_state_debt', ascending=False)
    n14 = n13.head(10)

    return n14