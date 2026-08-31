import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in03a'] == 1.0)].copy()
    n3 = tables['ii_vlh'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = tables['ii_portad'].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n7 = n4.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['vlh04'].isin([3.0, 4.0]))].copy()
    n9 = n8.groupby(['ent'], as_index=False).agg(unsafe_households=('vlh04', 'count'))
    n10 = pd.DataFrame({'mean_unsafe': [n9['unsafe_households'].mean()]})
    n10_mean_unsafe_value = n10['mean_unsafe'].iloc[0]
    n11 = n9[n9['unsafe_households'] >= n10_mean_unsafe_value].copy()
    n12 = n11.sort_values('unsafe_households', ascending=False)
    n13 = n12.head(5)
    n14 = n13[['ent', 'unsafe_households']].copy()

    return n14