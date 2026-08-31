import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 65.0)].copy()
    n3 = n1[(n1['edad'] < 18.0)].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = n4[(n4['edad_x'] >= 65.0) & (n4['edad_y'] < 18.0)].copy()
    n6 = n5[['folio', 'edad_x', 'edad_y']].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(pair_count=('folio', 'count'))
    n8 = tables['ii_se'].copy()
    n9 = n8[(n8['se01a'] == 1.0)].copy()
    n10 = n9[['folio']].copy()
    n11 = n10[n10['folio'].isin(n7['folio'])].copy()
    n12 = n11.groupby(['folio'], as_index=False).agg(household_rows=('folio', 'count'))
    n13 = pd.DataFrame({'households_with_both_ages_and_death': [n12['folio'].count()]})

    return n13