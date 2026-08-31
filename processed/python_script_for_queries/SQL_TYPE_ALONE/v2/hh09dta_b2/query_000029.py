import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = tables['ii_in'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = tables['ii_vlh'].copy()
    n5 = n4[(n4['vlh04'].isin([3.0, 4.0]))].copy()
    n6 = n3[n3['folio'].isin(n5['folio'])].copy()
    n7 = n6[(n6['in01a10_1_x'] == 1.0) & (n6['in02a10_x'] > 0.0) & (n6['in03a_y'] == 1.0)].copy()
    n8 = n7.merge(n5, left_on='folio', right_on='folio', how='inner')
    n9 = pd.DataFrame({'avg_vlh18a': [n4['vlh18a'].mean()]})
    n9_avg_vlh18a_value = n9['avg_vlh18a'].iloc[0]
    n10 = n8[n8['vlh18a'] > n9_avg_vlh18a_value].copy()
    n11 = tables['ii_portad'].copy()
    n12 = n10.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = n12[(n12['edad'] >= 18.0)].copy()
    n14 = n13.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'), n_individuals=('folio', 'count'))
    n15 = n14.sort_values('avg_age', ascending=False)

    return n15