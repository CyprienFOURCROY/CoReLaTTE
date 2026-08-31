import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n3 = n2[['folio', 'ent']].copy()
    n4 = tables['ii_vlh'].copy()
    n5 = n4.merge(n3, left_on='folio', right_on='folio', how='inner')
    n6 = n5[(n5['vlh18a'] > 0)].copy()
    n7 = n6.groupby(['ent'], as_index=False).agg(n_affected_households=('folio', 'count'), total_incidents_since_2005=('vlh18a', 'sum'))
    n8 = n7[(n7['n_affected_households'] >= 100)].copy()
    n9 = pd.DataFrame({'avg_total_incidents': [n7['total_incidents_since_2005'].mean()]})
    n9_avg_total_incidents_value = n9['avg_total_incidents'].iloc[0]
    n10 = n8[n8['total_incidents_since_2005'] > n9_avg_total_incidents_value].copy()
    n11 = n10.sort_values('total_incidents_since_2005', ascending=False)

    return n11