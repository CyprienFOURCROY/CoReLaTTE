import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n4 = tables['ii_su'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = tables['ii_crh'].copy()
    n7 = n6[(n6['crh04_1'] == 1)].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = pd.DataFrame({'overall_mean_debt': [n8['crh04_2'].mean()]})
    n9_overall_mean_debt_value = n9['overall_mean_debt'].iloc[0]
    n10 = n8[n8['crh04_2'] >= n9_overall_mean_debt_value].copy()
    n11 = n10.groupby(['su01'], as_index=False).agg(avg_debt=('crh04_2', 'mean'), n_households=('folio', 'count'))

    return n11