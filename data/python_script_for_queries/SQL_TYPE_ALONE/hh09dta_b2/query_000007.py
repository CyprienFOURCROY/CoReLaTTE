import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = tables['ii_in'].copy()
    n3 = n2[(n2['in03a'] == 1.0)].copy()
    n4 = n3[['folio']].copy()
    n5 = n1[n1['folio'].isin(n4['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6[(n6['edad'] >= 50.0)].copy()
    n8 = n7[['folio']].copy()
    n9 = n5[n5['folio'].isin(n8['folio'])].copy()
    n10 = n6[['folio', 'ent']].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n12 = n9.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = n12[(n12['vlh18a'] >= 0.0)].copy()
    n14 = n13.groupby(['ent'], as_index=False).agg(avg_vlh18a=('vlh18a', 'mean'), hh_count=('folio', 'count'))
    n15 = n14.sort_values('avg_vlh18a', ascending=False)
    n16 = n15.head(5)
    n17 = n13[n13['ent'].isin(n16['ent'])].copy()
    n18 = n17.groupby(['ent'], as_index=False).agg(avg_vlh18a=('vlh18a', 'mean'), households=('folio', 'count'))

    return n18