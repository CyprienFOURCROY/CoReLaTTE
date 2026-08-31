import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n3 = tables['ii_inr'].copy()
    n4 = n3[(n3['inr02a'] == 3.0) & (n3['inr02b'] == 3.0) & (n3['inr02c'] == 3.0) & (n3['inr02d'] == 3.0) & (n3['inr02e'] == 3.0) & (n3['inr02f'] == 3.0) & (n3['inr02g'] == 3.0) & (n3['inr02h'] == 3.0) & (n3['inr02i'] == 3.0) & (n3['inr02j'] == 3.0) & (n3['inr02k'] == 3.0)].copy()
    n5 = n4[['folio']].copy()
    n6 = tables['ii_vlh'].copy()
    n7 = n6[(n6['vlh08a'] == 1.0)].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.merge(n2, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['ent'], as_index=False).agg(n_eligible=('folio', 'count'))
    n11 = n10[(n10['n_eligible'] >= 30)].copy()
    n12 = n9[(n9['vlh04'].isin([3.0, 4.0]))].copy()
    n13 = n12.groupby(['ent'], as_index=False).agg(n_unsafe=('folio', 'count'))
    n14 = n13[n13['ent'].isin(n11['ent'])].copy()
    n15 = pd.DataFrame({'avg_unsafe': [n14['n_unsafe'].mean()]})
    n15_avg_unsafe_value = n15['avg_unsafe'].iloc[0]
    n16 = n14[n14['n_unsafe'] > n15_avg_unsafe_value].copy()
    n17 = n16.merge(n11, left_on='ent', right_on='ent', how='inner')
    n18 = n17.sort_values('n_unsafe', ascending=False)
    n19 = n18[['ent', 'n_eligible', 'n_unsafe']].copy()

    return n19