import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in01a11_1'] == 1.0)].copy()
    n3 = tables['ii_portad'].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n3[(n3['edad'] >= 70.0)].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(elder_count=('ls', 'count'), ent=('ent', 'min'))
    n8 = n5[n5['folio'].isin(n7['folio'])].copy()
    n9 = n8.groupby(['ent'], as_index=False).agg(n_elder_receiving_households=('folio', 'count'))
    n10 = pd.DataFrame({'avg_elder_receiving_by_state': [n9['n_elder_receiving_households'].mean()]})
    n10_avg_elder_receiving_by_state_value = n10['avg_elder_receiving_by_state'].iloc[0]
    n11 = n9[n9['n_elder_receiving_households'] >= n10_avg_elder_receiving_by_state_value].copy()
    n12 = n11[['ent', 'n_elder_receiving_households']].copy()

    return n12