import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n4 = pd.DataFrame({'avg_adult_count': [n3['adult_count'].mean()]})
    n4_avg_adult_count_value = n4['avg_adult_count'].iloc[0]
    n5 = n3[n3['adult_count'] > n4_avg_adult_count_value].copy()
    n6 = tables['ii_vlh'].copy()
    n7 = n6[(n6['vlh04'].isin([3.0, 4.0])) & (n6['vlh02_2'] <= 2005.0)].copy()
    n8 = n7[['folio']].copy()
    n9 = tables['ii_inr'].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(inr02b_min=('inr02b', 'min'))
    n11 = n10[(n10['inr02b_min'] == 1.0)].copy()
    n12 = n5[n5['folio'].isin(n8['folio'])].copy()
    n17 = n12.merge(n11, left_on='folio', right_on='folio', how='left')
    n18 = pd.DataFrame({'denominator_households': [n17['folio'].count()], 'numerator_households_produced_canned_goods': [n17['inr02b_min'].count()]})

    return n18