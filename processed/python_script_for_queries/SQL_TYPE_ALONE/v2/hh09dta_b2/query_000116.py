import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[['folio', 'ent']].copy()
    n3 = n2.groupby(['folio', 'ent'], as_index=False).agg(n_portad_rows=('folio', 'count'))
    n4 = n3[['folio', 'ent']].copy()
    n5 = tables['ii_su'].copy()
    n6 = n5[(n5['su01'] == 1.0)].copy()
    n7 = n4.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_inr'].copy()
    n9 = n8[['folio']].copy()
    n10 = n7[n7['folio'].isin(n9['folio'])].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(n_land_hh_inr=('folio', 'count'))
    n12 = n11[(n11['n_land_hh_inr'] >= 30)].copy()
    n13 = n10[['folio', 'ent']].copy()
    n14 = n8[(n8['inr02i'] == 1.0)].copy()
    n15 = n14[['folio']].copy()
    n16 = n13[n13['folio'].isin(n15['folio'])].copy()
    n17 = n16.groupby(['ent'], as_index=False).agg(n_honey=('folio', 'count'))
    n18 = n17[(n17['n_honey'] >= 10)].copy()
    n19 = n18[n18['ent'].isin(n12['ent'])].copy()
    n20 = n19.sort_values('n_honey', ascending=False)

    return n20