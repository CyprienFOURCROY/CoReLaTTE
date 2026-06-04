import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[['folio', 'ent']].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n4 = tables['ii_nna'].copy()
    n5 = n4[(n4['nna01'] == 1.0)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(nna_hh=('nna01', 'count'))
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_su'].copy()
    n9 = n8[(n8['su01'] == 1.0)].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(land_hh=('su01', 'count'))
    n11 = n7[n7['folio'].isin(n10['folio'])].copy()
    n12 = n11.groupby(['ent'], as_index=False).agg(households_both=('folio', 'count'))
    n13 = n12.sort_values('households_both', ascending=False)

    return n13