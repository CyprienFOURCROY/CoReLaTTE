import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20) & (n1['edad'] >= 30) & (n1['edad'] <= 60)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = n4[(n4['ah04e_2'] > 0) & (n4['ls_y'] == 2)].copy()
    n6 = tables['ii_in'].copy()
    n7 = n6[(n6['in02a10'] > 0)].copy()
    n8 = n5[n5['folio'].isin(n7['folio'])].copy()
    n9 = n8.groupby(['ent'], as_index=False).agg(avg_elec_value=('ah04e_2', 'mean'))
    n9_avg_elec_value_value = n9['avg_elec_value'].iloc[0]
    n10 = n8[n8['ah04e_2'] > n9_avg_elec_value_value].copy()
    n11 = n10[['folio', 'edad', 'ent', 'ls_x', 'ls_y', 'ah04e_2']].copy()
    n12 = n11.sort_values('ah04e_2', ascending=False)
    n13 = n12.head(10)

    return n13