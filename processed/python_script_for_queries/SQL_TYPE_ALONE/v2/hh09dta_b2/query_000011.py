import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh04_2'] > 0)].copy()
    n3 = tables['ii_su'].copy()
    n4 = n3[(n3['su01'] == 1)].copy()
    n5 = n4[n4['folio'].isin(n2['folio'])].copy()
    n6 = n5.merge(n2, left_on='folio', right_on='folio', how='inner')
    n7 = tables['ii_portad'].copy()
    n8 = n6.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = tables['ii_portad'].copy()
    n10 = n8.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10[(n10['edad_y'] >= 18)].copy()
    n12 = n11.groupby(['ent_y'], as_index=False).agg(avg_debt=('crh04_2', 'mean'), hh_count=('folio', 'count'))
    n13 = n12.sort_values('avg_debt', ascending=False)
    n14 = n13[['ent_y', 'avg_debt', 'hh_count']].copy()
    n15 = n14.head(10)

    return n15