import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_inr'].copy()
    n2 = n1[(n1['inr02j'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(seller_rows=('folio', 'count'))
    n4 = tables['ii_ah'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(bull_value=('ah04j_2', 'max'))
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = pd.DataFrame({'avg_bull_value_among_sellers': [n6['bull_value'].mean()]})
    n7_avg_bull_value_among_sellers_value = n7['avg_bull_value_among_sellers'].iloc[0]
    n8 = n6[n6['bull_value'] > n7_avg_bull_value_among_sellers_value].copy()
    n9 = tables['ii_portad'].copy()
    n10 = n9[(n9['edad'] >= 18.0)].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n12 = n8.merge(n11, left_on='folio', right_on='folio', how='inner')
    n13 = pd.DataFrame({'avg_adult_count_high_value_sellers': [n12['adult_count'].mean()]})

    return n13