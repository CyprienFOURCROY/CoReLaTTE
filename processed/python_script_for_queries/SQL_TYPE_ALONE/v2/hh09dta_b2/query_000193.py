import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = tables['ii_vlh'].copy()
    n4 = n3[(n3['vlh01k'] == 4)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_crh'].copy()
    n7 = n6[(n6['crh04c'] == 2)].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(adult_count=('folio', 'count'))

    return n9