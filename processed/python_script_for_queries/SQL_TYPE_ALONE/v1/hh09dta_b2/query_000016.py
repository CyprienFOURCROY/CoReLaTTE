import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03e'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_se'].copy()
    n5 = n4[(n4['se01d'] == 1.0)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8[n8['folio'].isin(n7['folio'])].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'), n_individuals=('folio', 'count'))
    n11 = n10.sort_values('avg_age', ascending=False)

    return n11