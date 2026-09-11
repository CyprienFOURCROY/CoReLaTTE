import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(max_edad=('edad', 'max'), ent=('ent', 'max'))
    n3 = n2[(n2['max_edad'] >= 60.0)].copy()
    n4 = n3[['folio', 'ent', 'max_edad']].copy()
    n5 = tables['ii_ah'].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(min_ah03d=('ah03d', 'min'))
    n7 = n6[(n6['min_ah03d'] == 1.0)].copy()
    n8 = tables['ii_su'].copy()
    n9 = n8[(n8['su01'] == 1.0)].copy()
    n10 = n9[['folio']].copy()
    n11 = n10[n10['folio'].isin(n4['folio'])].copy()
    n12 = n11[n11['folio'].isin(n7['folio'])].copy()
    n13 = tables['ii_in'].copy()
    n14 = n13[['folio', 'in02a10']].copy()
    n15 = n12.merge(n4, left_on='folio', right_on='folio', how='inner')
    n16 = n15.merge(n14, left_on='folio', right_on='folio', how='left')
    n17 = n16.groupby(['ent'], as_index=False).agg(avg_in02a10=('in02a10', 'mean'))
    n18 = n17.sort_values('avg_in02a10', ascending=True)

    return n18