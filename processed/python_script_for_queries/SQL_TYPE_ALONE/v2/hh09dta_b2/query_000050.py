import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n4 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n5 = tables['ii_in'].copy()
    n6 = n5[(n5['in01a10_1'] == 1.0) & (n5['in02a10'] > 0)].copy()
    n7 = n5[(n5['in03a'] == 1.0)].copy()
    n8 = n3[n3['folio'].isin(n7['folio'])].copy()
    n9 = pd.DataFrame({'liconsa_adult_mean': [n8['adult_count'].mean()]})
    n10 = n6.merge(n3, left_on='folio', right_on='folio', how='inner')
    n9_liconsa_adult_mean_value = n9['liconsa_adult_mean'].iloc[0]
    n11 = n10[n10['adult_count'] > n9_liconsa_adult_mean_value].copy()
    n12 = tables['ii_se'].copy()
    n13 = n12[(n12['se01b'] == 1.0)].copy()
    n14 = n11[n11['folio'].isin(n13['folio'])].copy()
    n15 = n14.merge(n4, left_on='folio', right_on='folio', how='inner')
    n16 = n15.groupby(['ent'], as_index=False).agg(avg_in02a10=('in02a10', 'mean'))
    n17 = n16.sort_values('avg_in02a10', ascending=False)

    return n17