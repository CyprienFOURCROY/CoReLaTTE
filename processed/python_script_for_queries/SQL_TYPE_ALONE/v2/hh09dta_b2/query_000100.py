import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n3 = n1[(n1['edad'] >= 70.0)].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(has70_count=('ls', 'count'))
    n5 = n4[['folio']].copy()
    n6 = tables['ii_in'].copy()
    n7 = n6[(n6['in02a11'] > 0.0)].copy()
    n8 = n6.merge(n2, left_on='folio', right_on='folio', how='left')
    n9 = n8[n8['folio'].isin(n5['folio'])].copy()
    n10 = n9[n9['folio'].isin(n7['folio'])].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(recipients_with_70plus=('folio', 'count'))
    n12 = n8[~n8['folio'].isin(n5['folio'])].copy()
    n13 = n12[n12['folio'].isin(n7['folio'])].copy()
    n14 = n13.groupby(['ent'], as_index=False).agg(recipients_without_70plus=('folio', 'count'))
    n15 = n11.merge(n14, left_on='ent', right_on='ent', how='outer')
    n16 = n15[['ent', 'recipients_with_70plus', 'recipients_without_70plus']].copy()

    return n16