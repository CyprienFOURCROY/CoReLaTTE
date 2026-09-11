import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1)].copy()
    n3 = tables['ii_crh'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = tables['ii_portad'].copy()
    n6 = n5[(n5['edad'] >= 18)].copy()
    n7 = n6.groupby(['folio', 'ent'], as_index=False).agg(adult_count=('ls', 'count'))
    n8 = n7[(n7['adult_count'] > 0)].copy()
    n9 = n8[['folio', 'ent']].copy()
    n10 = n4.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10[['ent', 'folio', 'crh02_1']].copy()
    n12 = n11[(n11['crh02_1'] == 1)].copy()
    n13 = n12.groupby(['ent'], as_index=False).agg(num_indebted_households=('folio', 'count'))
    n14 = pd.DataFrame({'avg_num_indebted': [n13['num_indebted_households'].mean()]})
    n14_avg_num_indebted_value = n14['avg_num_indebted'].iloc[0]
    n15 = n13[n13['num_indebted_households'] > n14_avg_num_indebted_value].copy()
    n16 = n15.sort_values('num_indebted_households', ascending=False)

    return n16