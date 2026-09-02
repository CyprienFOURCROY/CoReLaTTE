import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_nna'].copy()
    n2 = n1[(n1['nna01'] == 1)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n3[(n3['inr02a'] == 3) & (n3['inr02b'] == 3) & (n3['inr02c'] == 3) & (n3['inr02d'] == 3) & (n3['inr02e'] == 3) & (n3['inr02f'] == 3) & (n3['inr02g'] == 3) & (n3['inr02h'] == 3) & (n3['inr02i'] == 3) & (n3['inr02j'] == 3) & (n3['inr02k'] == 3)].copy()
    n5 = n4[n4['folio'].isin(n2['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n10 = n9[(n9['n_households'] >= 50)].copy()
    n11 = n10.sort_values('n_households', ascending=False)

    return n11