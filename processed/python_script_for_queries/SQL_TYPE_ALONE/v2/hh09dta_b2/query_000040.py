import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2[(n2['edad'] >= 18.0)].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(adult_count=('edad', 'count'))
    n5 = tables['ii_vlh'].copy()
    n6 = n5[(n5['vlh04'].isin([1.0, 2.0, 3.0, 4.0]))].copy()
    n7 = n2.groupby(['folio'], as_index=False).agg(hh_rows=('ls', 'count'))
    n8 = n6[n6['folio'].isin(n7['folio'])].copy()
    n9 = n8[n8['folio'].isin(n4['folio'])].copy()
    n10 = n9.merge(n4, left_on='folio', right_on='folio', how='inner')
    n11 = n10[['folio', 'vlh04', 'adult_count']].copy()
    n12 = n11.groupby(['vlh04'], as_index=False).agg(avg_adults_per_household=('adult_count', 'mean'))
    n13 = n12.sort_values('vlh04', ascending=True)

    return n13