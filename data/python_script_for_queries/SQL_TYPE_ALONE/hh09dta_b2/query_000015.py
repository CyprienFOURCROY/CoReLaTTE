import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_se'].copy()
    n5 = n4[(n4['se01a'] == 1)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = n4[(n4['se05_1h'] == 9)].copy()
    n9 = n8[['folio']].copy()
    n10 = n7[~n7['folio'].isin(n9['folio'])].copy()
    n11 = tables['ii_portad'].copy()
    n12 = n11[n11['folio'].isin(n10['folio'])].copy()
    n13 = n12.groupby(['ent'], as_index=False).agg(num_individuals=('ls', 'count'))
    n14 = n13.sort_values('num_individuals', ascending=False)

    return n14