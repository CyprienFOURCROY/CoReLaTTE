import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[['folio', 'ent']].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1)].copy()
    n6 = n5[['folio']].copy()
    n7 = tables['ii_inr'].copy()
    n8 = n7[(n7['inr02c'] == 3)].copy()
    n9 = n8[['folio', 'inr02c']].copy()
    n10 = tables['ii_crh'].copy()
    n11 = n10[['folio', 'crh03_2']].copy()
    n12 = n6.merge(n9, left_on='folio', right_on='folio', how='inner')
    n13 = n12.merge(n11, left_on='folio', right_on='folio', how='inner')
    n14 = n13.merge(n3, left_on='folio', right_on='folio', how='inner')
    n15 = n14[['ent', 'folio', 'crh03_2']].copy()
    n16 = n15.groupby(['ent'], as_index=False).agg(hh_count=('folio', 'count'), max_paid=('crh03_2', 'max'))
    n17 = n16[(n16['hh_count'] >= 25)].copy()
    n18 = pd.DataFrame({'avg_max_paid': [n17['max_paid'].mean()]})
    n18_avg_max_paid_value = n18['avg_max_paid'].iloc[0]
    n19 = n17[n17['max_paid'] > n18_avg_max_paid_value].copy()
    n20 = n19.sort_values('max_paid', ascending=False)
    n21 = n20[['ent', 'hh_count', 'max_paid']].copy()

    return n21