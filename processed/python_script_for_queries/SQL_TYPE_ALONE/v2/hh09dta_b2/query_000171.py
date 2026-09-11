import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n4 = tables['ii_vlh'].copy()
    n5 = n4[(n4['vlh04'].isin([1, 2, 3, 4]))].copy()
    n16 = tables['ii_nna'].copy()
    n17 = n16[(n16['nna01'] == 1)].copy()
    n18 = n5[n5['folio'].isin(n17['folio'])].copy()
    n6 = n18.merge(n3, left_on='folio', right_on='folio', how='inner')
    n7 = n6.groupby(['ent'], as_index=False).agg(total_hh=('folio', 'count'))
    n8 = n6[(n6['vlh02_2'] >= 2005)].copy()
    n9 = n8.groupby(['ent'], as_index=False).agg(recent_hh=('folio', 'count'))
    n10 = n7.merge(n9, left_on='ent', right_on='ent', how='left')
    n11 = n10[(n10['total_hh'] >= 30)].copy()
    n12 = pd.DataFrame({'avg_recent': [n11['recent_hh'].mean()]})
    n12_avg_recent_value = n12['avg_recent'].iloc[0]
    n13 = n11[n11['recent_hh'] >= n12_avg_recent_value].copy()
    n14 = n13[['ent', 'total_hh', 'recent_hh']].copy()
    n15 = n14.sort_values('recent_hh', ascending=False)

    return n15