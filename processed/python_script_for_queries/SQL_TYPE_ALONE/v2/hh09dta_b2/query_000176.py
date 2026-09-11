import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(state_code=('ent', 'min'))
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 1)].copy()
    n5 = n4[['folio']].copy()
    n6 = tables['ii_crh'].copy()
    n7 = n6[n6['folio'].isin(n5['folio'])].copy()
    n8 = n7[(n7['crh04_1'] == 1)].copy()
    n9 = n8.merge(n2, left_on='folio', right_on='folio', how='inner')
    n10 = pd.DataFrame({'overall_avg_debt': [n9['crh04_2'].mean()]})
    n10_overall_avg_debt_value = n10['overall_avg_debt'].iloc[0]
    n11 = n9[n9['crh04_2'] > n10_overall_avg_debt_value].copy()
    n12 = n11.groupby(['state_code'], as_index=False).agg(avg_total_debt=('crh04_2', 'mean'))
    n13 = n12[(n12['avg_total_debt'] > 10000)].copy()
    n14 = n13[['state_code', 'avg_total_debt']].copy()

    return n14