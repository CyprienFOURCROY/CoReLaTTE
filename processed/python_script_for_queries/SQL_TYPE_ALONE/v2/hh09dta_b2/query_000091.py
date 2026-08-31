import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in03a'] == 1)].copy()
    n3 = n2[['folio', 'in02a10']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4.groupby(['folio', 'ent'], as_index=False).agg(n_persons=('ls', 'count'))
    n6 = n5[['folio', 'ent']].copy()
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'), avg_other_prog=('in02a10', 'mean'))
    n9 = n8[(n8['n_households'] >= 25)].copy()
    n10 = n9[['ent']].copy()
    n11 = n7[n7['ent'].isin(n10['ent'])].copy()
    n12 = pd.DataFrame({'overall_avg_other_prog': [n11['in02a10'].mean()]})
    n12_overall_avg_other_prog_value = n12['overall_avg_other_prog'].iloc[0]
    n13 = n9[n9['avg_other_prog'] > n12_overall_avg_other_prog_value].copy()
    n14 = n13.sort_values('avg_other_prog', ascending=False)

    return n14