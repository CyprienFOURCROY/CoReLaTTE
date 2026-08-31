import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 30.0)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n3[(n3['inr02f'] == 1.0)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_vlh'].copy()
    n7 = n6[(n6['vlh04'].isin([1.0, 2.0]))].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8[['ent', 'ls_y', 'vlh04']].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(n_safe_craft_resp=('ls_y', 'count'))
    n11 = pd.DataFrame({'avg_state_safe_craft_resp': [n10['n_safe_craft_resp'].mean()]})
    n11_avg_state_safe_craft_resp_value = n11['avg_state_safe_craft_resp'].iloc[0]
    n12 = n10[n10['n_safe_craft_resp'] >= n11_avg_state_safe_craft_resp_value].copy()
    n13 = n12.sort_values('n_safe_craft_resp', ascending=False)
    n14 = n13[['ent', 'n_safe_craft_resp']].copy()

    return n14