import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh04'].isin([3.0, 4.0]))].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_in'].copy()
    n5 = n4[(n4['in02a10'] > 0)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8[n8['folio'].isin(n7['folio'])].copy()
    n10 = n9[['ent', 'edad']].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'), n_individuals=('edad', 'count'))
    n12 = n11.sort_values('avg_age', ascending=False)
    n13 = n12.head(10)

    return n13