import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh18a'] > 0)].copy()
    n3 = pd.DataFrame({'avg_incidents': [n2['vlh18a'].mean()]})
    n3_avg_incidents_value = n3['avg_incidents'].iloc[0]
    n4 = n2[n2['vlh18a'] > n3_avg_incidents_value].copy()
    n5 = n4[['folio']].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(households_above_avg=('folio', 'count'))
    n10 = n9.sort_values('households_above_avg', ascending=False)
    n11 = n10.head(5)

    return n11