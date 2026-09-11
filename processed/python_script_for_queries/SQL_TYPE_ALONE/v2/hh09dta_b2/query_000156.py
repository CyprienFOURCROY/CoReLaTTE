import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03d'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_vehicle_owners=('ls', 'count'))
    n4 = tables['ii_portad'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n6 = n3.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6.groupby(['ent'], as_index=False).agg(n_vehicle_households=('folio', 'count'))
    n8 = n7[(n7['n_vehicle_households'] >= 50)].copy()
    n9 = tables['ii_in'].copy()
    n10 = n3.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10[(n10['in02a10'] > 0)].copy()
    n12 = n11.merge(n5, left_on='folio', right_on='folio', how='inner')
    n13 = n12[n12['ent'].isin(n8['ent'])].copy()
    n14 = n13.groupby(['ent'], as_index=False).agg(avg_in02a10=('in02a10', 'mean'))
    n15 = n14.sort_values('avg_in02a10', ascending=False)

    return n15