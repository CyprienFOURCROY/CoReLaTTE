import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03d'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(mv_rows=('folio', 'count'))
    n5 = tables['ii_su'].copy()
    n6 = n5[(n5['su01'] == 1.0)].copy()
    n7 = n6[['folio']].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(plot_rows=('folio', 'count'))
    n9 = n4[n4['folio'].isin(n8['folio'])].copy()
    n10 = tables['ii_portad'].copy()
    n11 = n10[['folio', 'ent']].copy()
    n12 = n11.groupby(['folio', 'ent'], as_index=False).agg(hh_members=('folio', 'count'))
    n13 = n9.merge(n12, left_on='folio', right_on='folio', how='inner')
    n14 = n13.groupby(['ent'], as_index=False).agg(num_hh=('folio', 'count'))
    n15 = n4.merge(n12, left_on='folio', right_on='folio', how='inner')
    n16 = n15.groupby(['ent'], as_index=False).agg(den_hh=('folio', 'count'))
    n17 = n16[(n16['den_hh'] >= 20)].copy()
    n18 = n14[n14['ent'].isin(n17['ent'])].copy()
    n19 = pd.DataFrame({'mean_num_hh': [n18['num_hh'].mean()]})
    n19_mean_num_hh_value = n19['mean_num_hh'].iloc[0]
    n20 = n18[n18['num_hh'] > n19_mean_num_hh_value].copy()

    return n20