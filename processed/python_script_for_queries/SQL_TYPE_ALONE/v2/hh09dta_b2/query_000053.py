import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_vlh'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = tables['ii_nna'].copy()
    n5 = n3.merge(n4, left_on='folio_x', right_on='folio', how='inner')
    n6 = n5[(n5['vlh04'].isin([3.0, 4.0])) & (n5['nna01'].isin([1.0, 2.0]))].copy()
    n7 = n6.groupby(['ent', 'folio_x'], as_index=False).agg(nna01_hh=('nna01', 'max'))
    n8 = tables['ii_su'].copy()
    n9 = n8[(n8['su01'] == 3.0)].copy()
    n10 = n7[n7['folio_x'].isin(n9['folio'])].copy()
    n11 = n10[(n10['nna01_hh'] == 1.0)].copy()
    n12 = n11.groupby(['ent'], as_index=False).agg(yes_households=('folio_x', 'count'))
    n13 = pd.DataFrame({'avg_yes_per_state': [n12['yes_households'].mean()]})
    n14 = n12[(n12['ent'].isin([20.0, 21.0]))].copy()
    n13_avg_yes_per_state_value = n13['avg_yes_per_state'].iloc[0]
    n15 = n14[n14['yes_households'] < n13_avg_yes_per_state_value].copy()
    n16 = n15.sort_values('yes_households', ascending=True)
    n17 = n16[['ent', 'yes_households']].copy()

    return n17