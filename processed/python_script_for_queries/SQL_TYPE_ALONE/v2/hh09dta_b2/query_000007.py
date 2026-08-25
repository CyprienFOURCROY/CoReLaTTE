import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh04'].isin([3, 4]))].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = n5.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'), n_individuals=('edad', 'count'))
    n7 = n6[(n6['n_individuals'] >= 10)].copy()
    n8 = n7.sort_values('avg_age', ascending=False)

    return n8