import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(num_individuals=('ls', 'count'))
    n4 = tables['ii_crh'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = n5[(n5['crh03_1'] == 1.0) & (n5['crh03_2'] != None)].copy()
    n7 = tables['ii_vlh'].copy()
    n8 = n7[(n7['vlh04'].isin([3.0, 4.0]))].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(unsafe_marker_count=('vlh04', 'count'))
    n10 = n4[n4['folio'].isin(n9['folio'])].copy()
    n11 = n10[(n10['crh03_1'] == 1.0) & (n10['crh03_2'] != None)].copy()
    n12 = pd.DataFrame({'avg_unsafe_payment': [n11['crh03_2'].mean()]})
    n12_avg_unsafe_payment_value = n12['avg_unsafe_payment'].iloc[0]
    n13 = n6[n6['crh03_2'] > n12_avg_unsafe_payment_value].copy()
    n14 = n13[['folio', 'crh03_2']].copy()
    n15 = n14.sort_values('crh03_2', ascending=False)

    return n15