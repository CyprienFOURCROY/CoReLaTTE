import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in01a10_1'] == 1)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4[(n4['edad'] >= 30) & (n4['edad'] <= 50)].copy()
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = tables['ii_ah'].copy()
    n8 = n6.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8[(n8['ls_x'].isin(['01', '02']))].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_wash_stove_value=('ah04f_2', 'mean'))
    n11 = pd.DataFrame({'mean_of_state_avg': [n10['avg_wash_stove_value'].mean()]})
    n11_mean_of_state_avg_value = n11['mean_of_state_avg'].iloc[0]
    n12 = n10[n10['avg_wash_stove_value'] > n11_mean_of_state_avg_value].copy()
    n13 = n12.sort_values('avg_wash_stove_value', ascending=False)
    n14 = n13[['ent', 'avg_wash_stove_value']].copy()

    return n14