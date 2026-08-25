import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent_state=('ent', 'min'))
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 1)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = tables['ii_vlh'].copy()
    n7 = n6[['folio', 'vlh04']].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8[(n8['vlh04'].isin([1, 2, 3, 4]))].copy()
    n10 = n9.groupby(['ent_state'], as_index=False).agg(avg_vlh04=('vlh04', 'mean'), n_households=('folio', 'count'))
    n11 = n10[(n10['n_households'] >= 2)].copy()
    n12 = n11.sort_values('avg_vlh04', ascending=True)
    n13 = n12.head(5)

    return n13