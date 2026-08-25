import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2[['folio', 'ent', 'edad']].copy()
    n4 = tables['ii_crh'].copy()
    n5 = n4[(n4['crh04_1'] == 1) & (n4['crh04_2'] > 0)].copy()
    n6 = n5[['folio', 'crh04_2']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_su'].copy()
    n9 = n8[(n8['su01'] == 1)].copy()
    n10 = n9[['folio', 'su01']].copy()
    n11 = n7.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11.merge(n6, left_on='folio', right_on='folio', how='inner')
    n13 = n12.groupby(['ent'], as_index=False).agg(avg_debt=('crh04_2', 'mean'), num_records=('folio', 'count'))
    n14 = n13.sort_values('avg_debt', ascending=False)
    n15 = n14.head(10)

    return n15