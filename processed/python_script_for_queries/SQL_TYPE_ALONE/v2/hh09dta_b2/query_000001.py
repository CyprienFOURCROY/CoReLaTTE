import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n3 = tables['ii_vlh'].copy()
    n4 = n3.merge(n2, left_on='folio', right_on='folio', how='inner')
    n5 = n4[(n4['vlh08a'] == 1.0)].copy()
    n6 = n5.groupby(['ent'], as_index=False).agg(n_households_reporting_robbery_friends=('folio', 'count'))
    n7 = n6[(n6['n_households_reporting_robbery_friends'] >= 5)].copy()
    n8 = n7[['ent']].copy()
    n9 = n4[n4['ent'].isin(n8['ent'])].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_home_safety=('vlh04', 'mean'), total_households_in_state=('folio', 'count'), avg_leave_lights_code=('vlh06', 'mean'))
    n11 = n10.sort_values('avg_home_safety', ascending=True)

    return n11