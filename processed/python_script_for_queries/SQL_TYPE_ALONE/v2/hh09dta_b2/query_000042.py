import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah04g_1'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(hh_max_appliance_value=('ah04g_2', 'max'))
    n4 = tables['ii_nna'].copy()
    n5 = n4[(n4['nna01'] == 1.0)].copy()
    n6 = n4[(n4['nna01'] == 2.0)].copy()
    n7 = tables['ii_portad'].copy()
    n8 = n7[(n7['ent'] == 20.0)].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(members_in_oax=('folio', 'count'))
    n10 = n3[n3['folio'].isin(n5['folio'])].copy()
    n11 = n10[n10['folio'].isin(n9['folio'])].copy()
    n12 = n3[n3['folio'].isin(n6['folio'])].copy()
    n13 = n12[n12['folio'].isin(n9['folio'])].copy()
    n14 = pd.DataFrame({'avg_oax_nonbiz_max_appliance_value': [n13['hh_max_appliance_value'].mean()]})
    n14_avg_oax_nonbiz_max_appliance_value_value = n14['avg_oax_nonbiz_max_appliance_value'].iloc[0]
    n15 = n11[n11['hh_max_appliance_value'] > n14_avg_oax_nonbiz_max_appliance_value_value].copy()
    n16 = n15[['folio', 'hh_max_appliance_value']].copy()
    n17 = n16.sort_values('hh_max_appliance_value', ascending=False)

    return n17