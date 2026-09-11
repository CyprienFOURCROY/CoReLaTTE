import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_adults18plus=('ls', 'count'))
    n4 = tables['ii_su'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_crh'].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['crh04_1'] == 1.0) & (n7['su01'].isin([1.0, 3.0]))].copy()
    n9 = n8.groupby(['su01'], as_index=False).agg(avg_total_debt=('crh04_2', 'mean'))
    n10 = pd.DataFrame({'overall_avg_total_debt': [n8['crh04_2'].mean()]})
    n10_overall_avg_total_debt_value = n10['overall_avg_total_debt'].iloc[0]
    n11 = n9[n9['avg_total_debt'] > n10_overall_avg_total_debt_value].copy()
    n12 = n11.sort_values('avg_total_debt', ascending=False)

    return n12