import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_se'].copy()
    n5 = n4[(n4['se01e'] == 1)].copy()
    n6 = n5[['folio']].copy()
    n7 = tables['ii_portad'].copy()
    n8 = n7[n7['folio'].isin(n3['folio'])].copy()
    n9 = n8[n8['folio'].isin(n6['folio'])].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'), num_individuals=('folio', 'count'))
    n11 = n10.sort_values('avg_age', ascending=False)

    return n11