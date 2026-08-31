import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01b'] == 1.0)].copy()
    n3 = tables['ii_vlh'].copy()
    n4 = n3[(n3['vlh04'].isin([3.0, 4.0]))].copy()
    n5 = n4[n4['folio'].isin(n2['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent_state=('ent', 'min'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent_state'], as_index=False).agg(n_households_unsafe_disease=('folio', 'count'))
    n10 = n9[(n9['n_households_unsafe_disease'] >= 50)].copy()

    return n10