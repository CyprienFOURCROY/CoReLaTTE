import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18.0)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = tables['ii_in'].copy()
    n6 = n4.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6[['ent', 'folio', 'edad', 'ls_y', 'inr02j', 'in01a10_1']].copy()
    n8 = n7[(n7['inr02j'] == 1.0) & (n7['in01a10_1'] == 1.0)].copy()
    n9 = n8.groupby(['ent'], as_index=False).agg(qualified_adults=('folio', 'count'))
    n10 = pd.DataFrame({'avg_qualified_adults': [n9['qualified_adults'].mean()]})
    n10_avg_qualified_adults_value = n10['avg_qualified_adults'].iloc[0]
    n11 = n9[n9['qualified_adults'] > n10_avg_qualified_adults_value].copy()
    n12 = n11.sort_values('qualified_adults', ascending=False)

    return n12