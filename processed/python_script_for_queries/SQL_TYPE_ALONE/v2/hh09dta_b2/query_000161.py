import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 70)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(elderly_count=('ls', 'count'), state=('ent', 'max'))
    n4 = tables['ii_in'].copy()
    n5 = n4[(n4['in01a11_1'] == 1)].copy()
    n6 = tables['ii_vlh'].copy()
    n7 = n6[(n6['vlh04'].isin([3, 4]))].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n6[(n6['vlh10c'] == 1)].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(kidnap_yes_count=('vlh10c', 'count'))
    n11 = n8[~n8['folio'].isin(n10['folio'])].copy()
    n12 = n11.merge(n3, left_on='folio', right_on='folio', how='inner')
    n13 = n12.groupby(['state'], as_index=False).agg(hh_count=('folio', 'count'))
    n14 = n13[(n13['hh_count'] >= 10)].copy()
    n15 = n14.sort_values('hh_count', ascending=False)
    n16 = n15[['state', 'hh_count']].copy()

    return n16