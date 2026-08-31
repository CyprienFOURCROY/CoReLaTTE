import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_ah'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3[(n3['ls_x'] == '01') & (n3['ah04e_1'] == 1)].copy()
    n5 = tables['ii_in'].copy()
    n6 = n5[(n5['in03a'] == 1)].copy()
    n7 = n4[n4['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_vlh'].copy()
    n9 = n7.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9[(n9['vlh04'].isin([1, 2]))].copy()
    n11 = n10.groupby(['folio', 'ent'], as_index=False).agg(hh_ah04e2_sum=('ah04e_2', 'sum'))
    n12 = n11.groupby(['ent'], as_index=False).agg(mean_ah04e2=('hh_ah04e2_sum', 'mean'))
    n13 = pd.DataFrame({'global_mean_ah04e2': [n11['hh_ah04e2_sum'].mean()]})
    n13_global_mean_ah04e2_value = n13['global_mean_ah04e2'].iloc[0]
    n14 = n12[n12['mean_ah04e2'] > n13_global_mean_ah04e2_value].copy()
    n15 = n14.sort_values('mean_ah04e2', ascending=False)

    return n15