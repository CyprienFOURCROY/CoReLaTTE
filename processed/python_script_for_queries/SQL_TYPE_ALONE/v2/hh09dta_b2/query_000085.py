import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03e'] == 1)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(device_members=('ah03e', 'count'))
    n4 = tables['ii_portad'].copy()
    n5 = n4[(n4['edad'] >= 18)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(adult_members=('ls', 'count'))
    n7 = n6[n6['folio'].isin(n3['folio'])].copy()
    n8 = n4.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n9 = n7.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = tables['ii_vlh'].copy()
    n11 = n10[(n10['vlh04'].isin([1, 2]))].copy()
    n12 = n9.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = n12.groupby(['ent'], as_index=False).agg(safe_qual_hh=('folio', 'count'))
    n14 = pd.DataFrame({'avg_safe_per_state': [n13['safe_qual_hh'].mean()]})
    n14_avg_safe_per_state_value = n14['avg_safe_per_state'].iloc[0]
    n15 = n13[n13['safe_qual_hh'] > n14_avg_safe_per_state_value].copy()
    n16 = n15.sort_values('safe_qual_hh', ascending=False)

    return n16