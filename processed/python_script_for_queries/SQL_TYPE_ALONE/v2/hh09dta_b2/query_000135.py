import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(hh_size=('ls', 'count'))
    n3 = pd.DataFrame({'avg_hh_size': [n2['hh_size'].mean()]})
    n3_avg_hh_size_value = n3['avg_hh_size'].iloc[0]
    n4 = n2[n2['hh_size'] > n3_avg_hh_size_value].copy()
    n5 = tables['ii_ah'].copy()
    n6 = n5[(n5['ah03d'] == 1.0)].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(num_vehicle_owners=('ls', 'count'))
    n8 = n4[n4['folio'].isin(n7['folio'])].copy()
    n9 = tables['ii_vlh'].copy()
    n10 = n9[(n9['vlh04'] == 1.0)].copy()
    n11 = n8[n8['folio'].isin(n10['folio'])].copy()
    n12 = tables['ii_crh'].copy()
    n12a = n12[(n12['crh04_1'] == 1.0)].copy()
    n13 = n11.merge(n12a, left_on='folio', right_on='folio', how='inner')
    n14 = n13[['folio', 'crh04_2']].copy()
    n15 = pd.DataFrame({'avg_total_debt': [n14['crh04_2'].mean()]})

    return n15