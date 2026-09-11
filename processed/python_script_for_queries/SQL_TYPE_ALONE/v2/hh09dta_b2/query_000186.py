import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1.0)].copy()
    n3 = tables['ii_crh'].copy()
    n4 = n3[(n3['crh04_1'] == 1.0)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio', 'ent'], as_index=False).agg(n_members=('ls', 'count'))
    n8 = n7[['folio', 'ent']].copy()
    n9 = n5.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'), avg_debt=('crh04_2', 'mean'))
    n11 = n10[(n10['n_households'] >= 20)].copy()
    n12 = pd.DataFrame({'overall_avg_debt': [n9['crh04_2'].mean()]})
    n12_overall_avg_debt_value = n12['overall_avg_debt'].iloc[0]
    n13 = n11[n11['avg_debt'] > n12_overall_avg_debt_value].copy()
    n14 = n13.sort_values('avg_debt', ascending=False)
    n15 = n14[['ent', 'n_households', 'avg_debt']].copy()

    return n15