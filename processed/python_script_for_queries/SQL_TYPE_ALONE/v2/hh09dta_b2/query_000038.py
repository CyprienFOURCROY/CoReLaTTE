import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n3[(n3['ah03d'] == 1.0)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n7 = tables['ii_vlh'].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['folio'], as_index=False).agg(qualifying_adults=('ls', 'count'))
    n10 = n1[(n1['ent'] == 20.0)].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(household_members=('ls', 'count'))
    n12 = n11.merge(n7, left_on='folio', right_on='folio', how='inner')
    n13 = n12[(n12['vlh04'].isin([3.0, 4.0]))].copy()
    n14 = n13.merge(n9, left_on='folio', right_on='folio', how='left')
    n15 = pd.DataFrame({'total_unsafe_households': [n14['folio'].count()], 'unsafe_with_adult_vehicle_owner': [n14['qualifying_adults'].count()]})

    return n15