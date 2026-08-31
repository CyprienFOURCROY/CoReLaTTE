import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_nna'].copy()
    n2 = n1[(n1['nna01'] == 1)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n3[(n3['inr02d'] == 1)].copy()
    n5 = n4[n4['folio'].isin(n2['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(member_count=('ls', 'count'), ent=('ent', 'min'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent', 'member_count'], as_index=False).agg(household_count=('folio', 'count'))
    n10 = pd.DataFrame({'max_household_count': [n9['household_count'].max()]})
    n10_max_household_count_value = n10['max_household_count'].iloc[0]
    n11 = n9[n9['household_count'] == n10_max_household_count_value].copy()
    n12 = n11.sort_values('household_count', ascending=False)
    n13 = n12[['ent', 'member_count', 'household_count']].copy()

    return n13