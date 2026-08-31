import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in02a10'] > 0)].copy()
    n3 = tables['ii_vlh'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = tables['ii_portad'].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n7 = n4.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['vlh18a'] >= 0)].copy()
    n9 = n8.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'), mean_rob_since_2005=('vlh18a', 'mean'))
    n10 = n9[(n9['n_households'] >= 30)].copy()
    n11 = pd.DataFrame({'global_mean_rob': [n8['vlh18a'].mean()]})
    n11_global_mean_rob_value = n11['global_mean_rob'].iloc[0]
    n12 = n10[n10['mean_rob_since_2005'] > n11_global_mean_rob_value].copy()
    n13 = n12[['ent', 'n_households', 'mean_rob_since_2005']].copy()

    return n13