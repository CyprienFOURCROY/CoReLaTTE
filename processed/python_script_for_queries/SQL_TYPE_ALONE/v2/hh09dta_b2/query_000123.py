import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in01a10_1'] == 1.0) & (n1['in02a10'] > 0.0)].copy()
    n3 = tables['ii_vlh'].copy()
    n4 = n3[(n3['vlh04'].isin([3.0, 4.0]))].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_ah'].copy()
    n7 = n6[(n6['ah03d'] == 1.0)].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(has_car_count=('ah03d', 'count'))
    n9 = n5.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = tables['ii_portad'].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n12 = n9.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = n12.groupby(['ent'], as_index=False).agg(qualified_count=('folio', 'count'))
    n14 = pd.DataFrame({'avg_qualified_per_state': [n13['qualified_count'].mean()]})
    n14_avg_qualified_per_state_value = n14['avg_qualified_per_state'].iloc[0]
    n15 = n13[n13['qualified_count'] > n14_avg_qualified_per_state_value].copy()
    n16 = n15.sort_values('qualified_count', ascending=False)
    n17 = n16[['ent', 'qualified_count']].copy()

    return n17