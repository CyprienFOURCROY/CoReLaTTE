import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1)].copy()
    n6 = n5[['folio', 'su231']].copy()
    n7 = tables['ii_se'].copy()
    n8 = n7[(n7['se01e'] == 1)].copy()
    n9 = tables['ii_in'].copy()
    n10 = n9[(n9['in01a10_1'] == 3)].copy()
    n11 = n6[n6['folio'].isin(n8['folio'])].copy()
    n12 = n11[n11['folio'].isin(n10['folio'])].copy()
    n13 = n12.merge(n3, left_on='folio', right_on='folio', how='inner')
    n14 = n13.groupby(['adult_count'], as_index=False).agg(avg_su231=('su231', 'mean'), household_count=('folio', 'count'))
    n15 = n14.sort_values('adult_count', ascending=True)

    return n15