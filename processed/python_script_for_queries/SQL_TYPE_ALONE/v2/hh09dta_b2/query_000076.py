import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 1.0)].copy()
    n5 = n4[['folio']].copy()
    n6 = n2[n2['folio'].isin(n5['folio'])].copy()
    n7 = tables['ii_vlh'].copy()
    n8 = n7[(n7['vlh04'].isin([1.0, 2.0, 3.0, 4.0]))].copy()
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9[['ent', 'folio', 'vlh04']].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'), avg_vlh04=('vlh04', 'mean'))
    n12 = n11[(n11['n_households'] >= 30)].copy()
    n13 = n12.sort_values('avg_vlh04', ascending=True)

    return n13