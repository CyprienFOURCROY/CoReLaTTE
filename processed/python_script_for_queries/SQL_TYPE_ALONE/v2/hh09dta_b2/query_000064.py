import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18.0)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = n4[['folio', 'ent', 'edad', 'inr02a', 'ls_x', 'ls_y']].copy()
    n6 = tables['ii_in'].copy()
    n7 = n6[(n6['in03a'].isin([1.0, 3.0]))].copy()
    n8 = n5[n5['folio'].isin(n7['folio'])].copy()
    n9 = n8[(n8['inr02a'] == 1.0)].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(sold_dairy_adults=('folio', 'count'))
    n11 = pd.DataFrame({'avg_sold_dairy_adults': [n10['sold_dairy_adults'].mean()]})
    n11_avg_sold_dairy_adults_value = n11['avg_sold_dairy_adults'].iloc[0]
    n12 = n10[n10['sold_dairy_adults'] > n11_avg_sold_dairy_adults_value].copy()
    n13 = n12.sort_values('sold_dairy_adults', ascending=False)
    n14 = n13[['ent', 'sold_dairy_adults']].copy()

    return n14