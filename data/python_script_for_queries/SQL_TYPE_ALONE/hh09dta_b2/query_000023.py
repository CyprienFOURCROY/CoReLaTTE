import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_nna'].copy()
    n5 = n4[(n4['nna01'] == 1.0)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8[(n8['edad'] >= 18.0)].copy()
    n10 = n9[n9['folio'].isin(n7['folio'])].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(count_individuals=('edad', 'count'))
    n12 = n11.sort_values('count_individuals', ascending=False)
    n13 = n12.head(1)
    n14 = n11[n11['count_individuals'].isin(n13['count_individuals'])].copy()

    return n14