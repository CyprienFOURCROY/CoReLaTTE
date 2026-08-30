import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 1)].copy()
    n5 = tables['ii_se'].copy()
    n6 = n5[(n5['se01e'] == 1)].copy()
    n7 = n4[n4['folio'].isin(n6['folio'])].copy()
    n8 = n7.merge(n2, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(hh_count=('folio', 'count'))
    n10 = n9.sort_values('hh_count', ascending=False)

    return n10