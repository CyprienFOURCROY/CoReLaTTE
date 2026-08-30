import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_inr'].copy()
    n2 = n1[(n1['inr02a'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_dairy_producers=('inr02a', 'count'))
    n4 = tables['ii_portad'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(hh_avg_age=('edad', 'mean'), ent=('ent', 'min'))
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = n6.groupby(['ent'], as_index=False).agg(n_producing_hh=('folio', 'count'), avg_hh_age_producers=('hh_avg_age', 'mean'))
    n8 = tables['ii_nna'].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(nna01_min=('nna01', 'min'))
    n10 = n6.merge(n9, left_on='folio', right_on='folio', how='left')
    n11 = n10[(n10['nna01_min'] == 1.0)].copy()
    n12 = n11.groupby(['ent'], as_index=False).agg(n_hh_with_nonag=('folio', 'count'))
    n13 = n7.merge(n12, left_on='ent', right_on='ent', how='left')
    n14 = n13.sort_values('n_producing_hh', ascending=False)
    n15 = n14.head(10)

    return n15