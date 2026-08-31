import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_inr'].copy()
    n2 = n1[(n1['inr04d'] > 0.0)].copy()
    n3 = tables['ii_portad'].copy()
    n4 = n3[(n3['ent'] == 20.0)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = tables['ii_su'].copy()
    n7 = n6[(n6['su01'] == 1.0)].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = tables['ii_nna'].copy()
    n10 = n9[(n9['nna01'] == 2.0)].copy()
    n11 = n8.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = tables['ii_inr'].copy()
    n13 = n12[(n12['inr04d'] > 0.0)].copy()
    n14 = n13[n13['folio'].isin(n4['folio'])].copy()
    n15 = n14.merge(n7, left_on='folio', right_on='folio', how='inner')
    n16 = n9[(n9['nna01'] == 1.0)].copy()
    n17 = n15.merge(n16, left_on='folio', right_on='folio', how='inner')
    n18 = pd.DataFrame({'avg_inr04d_ref': [n17['inr04d'].mean()]})
    n18_avg_inr04d_ref_value = n18['avg_inr04d_ref'].iloc[0]
    n19 = n11[n11['inr04d'] > n18_avg_inr04d_ref_value].copy()
    n20 = n19[['folio', 'inr04d']].copy()
    n21 = n20.sort_values('inr04d', ascending=False)

    return n21