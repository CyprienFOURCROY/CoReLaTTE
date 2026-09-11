import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = tables['ii_su'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = tables['ii_portad'].copy()
    n5 = n4[(n4['ent'] == 20.0) & (n4['edad'] >= 60.0)].copy()
    n6 = n3.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6[(n6['su01'] == 1.0) & (n6['in01a10_1'] == 1.0)].copy()
    n8 = tables['ii_nna'].copy()
    n9 = n8[(n8['nna01'] == 1.0)].copy()
    n10 = n7[n7['folio'].isin(n9['folio'])].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(ogp_amt=('in02a10', 'mean'))
    n12 = pd.DataFrame({'avg_ogp_amt': [n11['ogp_amt'].mean()]})
    n12_avg_ogp_amt_value = n12['avg_ogp_amt'].iloc[0]
    n13 = n11[n11['ogp_amt'] > n12_avg_ogp_amt_value].copy()
    n14 = n13.sort_values('ogp_amt', ascending=False)
    n15 = n14[['folio', 'ogp_amt']].copy()

    return n15