import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 18.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(adult_count=('folio', 'count'))
    n5 = tables['ii_inr'].copy()
    n6 = n5[(n5['inr02d'] == 1.0)].copy()
    n7 = n6[['folio']].copy()
    n8 = n4.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = tables['ii_nna'].copy()
    n10 = n9[(n9['nna01'] == 1.0)].copy()
    n11 = n10[['folio']].copy()
    n12 = n8[n8['folio'].isin(n11['folio'])].copy()
    n13 = n12.merge(n9, left_on='folio', right_on='folio', how='inner')
    n14 = pd.DataFrame({'min_nna02': [n13['nna02'].min()]})
    n14_min_nna02_value = n14['min_nna02'].iloc[0]
    n15 = n13[n13['nna02'] >= n14_min_nna02_value].copy()
    n16 = pd.DataFrame({'avg_nna02': [n15['nna02'].mean()]})

    return n16