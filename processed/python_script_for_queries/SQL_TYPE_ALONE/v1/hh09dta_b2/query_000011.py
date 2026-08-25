import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_inr'].copy()
    n2 = n1[(n1['inr02a'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1.0)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[~n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8[['folio', 'ent', 'edad']].copy()
    n10 = n9[n9['folio'].isin(n7['folio'])].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(num_individuals=('folio', 'count'), avg_age=('edad', 'mean'))
    n12 = n11.sort_values('num_individuals', ascending=False)

    return n12