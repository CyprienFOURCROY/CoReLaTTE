import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh04_1'] == 1)].copy()
    n3 = pd.DataFrame({'overall_avg_debt': [n2['crh04_2'].mean()]})
    n4 = tables['ii_crh'].copy()
    n5 = n4[(n4['crh04_1'] == 1)].copy()
    n6 = n5[['folio', 'crh04_2']].copy()
    n7 = tables['ii_portad'].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(ent_state=('ent', 'min'))
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['ent_state'], as_index=False).agg(avg_debt=('crh04_2', 'mean'), households=('folio', 'count'))
    n3_overall_avg_debt_value = n3['overall_avg_debt'].iloc[0]
    n11 = n10[n10['avg_debt'] > n3_overall_avg_debt_value].copy()
    n12 = n11.sort_values('avg_debt', ascending=False)

    return n12