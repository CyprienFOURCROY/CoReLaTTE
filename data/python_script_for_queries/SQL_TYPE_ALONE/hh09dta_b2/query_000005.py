import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01d'] == 1)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1)].copy()
    n6 = n5[['folio']].copy()
    n7 = tables['ii_portad'].copy()
    n8 = n7[n7['folio'].isin(n3['folio'])].copy()
    n9 = n8[n8['folio'].isin(n6['folio'])].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'), n_individuals=('edad', 'count'))
    n13 = n10.sort_values('avg_age', ascending=False)
    n14 = n13[['ent', 'avg_age', 'n_individuals']].copy()

    return n14