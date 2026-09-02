import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03d'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(num_vehicle_owners=('ah03d', 'count'))
    n4 = n3[['folio']].copy()
    n5 = tables['ii_portad'].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n7 = tables['ii_vlh'].copy()
    n8 = n7[n7['folio'].isin(n4['folio'])].copy()
    n9 = n8.merge(n6, left_on='folio', right_on='folio', how='inner')
    n10 = n9[(n9['ent'] == 20.0)].copy()
    n11 = n9[(n9['ent'] != 20.0)].copy()
    n12 = pd.DataFrame({'mean_vlh04_non_oax': [n11['vlh04'].mean()]})
    n12_mean_vlh04_non_oax_value = n12['mean_vlh04_non_oax'].iloc[0]
    n13 = n10[n10['vlh04'] > n12_mean_vlh04_non_oax_value].copy()
    n14 = n13[['folio', 'vlh04', 'ent']].copy()
    n15 = n14.sort_values('vlh04', ascending=False)

    return n15