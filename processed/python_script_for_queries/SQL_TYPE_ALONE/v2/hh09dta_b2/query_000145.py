import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18.0) & (n1['edad'] <= 29.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(youth_count=('ls', 'count'))
    n4 = tables['ii_vlh'].copy()
    n5 = n4[(n4['vlh18a'] > 0.0)].copy()
    n6 = n5[['folio']].copy()
    n7 = n6.merge(n3, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_se'].copy()
    n9 = n8[(n8['se01a'] == 3.0) & (n8['se01b'] == 3.0) & (n8['se01c'] == 3.0) & (n8['se01d'] == 3.0) & (n8['se01e'] == 3.0) & (n8['se01f'] == 3.0)].copy()
    n10 = n9[['folio']].copy()
    n11 = n8[['folio']].copy()
    n12 = n11[~n11['folio'].isin(n10['folio'])].copy()
    n13 = n7[n7['folio'].isin(n12['folio'])].copy()
    n14 = tables['ii_nna'].copy()
    n15 = n14[['folio', 'nna02']].copy()
    n16 = n13.merge(n15, left_on='folio', right_on='folio', how='left')
    n17 = pd.DataFrame({'avg_nna02_anyshock': [n16['nna02'].mean()]})

    return n17