import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20)].copy()
    n3 = n2[['folio', 'ls', 'edad', 'ent']].copy()
    n4 = tables['ii_se'].copy()
    n5 = n4[(n4['se01b'] == 1)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_inr'].copy()
    n9 = n8[(n8['inr02d'] == 1)].copy()
    n10 = n9[['folio']].copy()
    n11 = n7[n7['folio'].isin(n10['folio'])].copy()
    n14 = n11.groupby(['folio'], as_index=False).agg(avg_edad_household=('edad', 'mean'), num_individuals=('edad', 'count'))
    n15 = n14.sort_values('avg_edad_household', ascending=False)
    n16 = n15.head(5)

    return n16