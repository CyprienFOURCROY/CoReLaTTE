import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ls'] == '01') & (n1['edad'] >= 30)].copy()
    n3 = n2[['folio', 'ent']].copy()
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1)].copy()
    n6 = n5[['folio', 'su234']].copy()
    n7 = tables['ii_nna'].copy()
    n8 = n7[(n7['nna01'] == 1)].copy()
    n9 = n8[['folio']].copy()
    n10 = n3[n3['folio'].isin(n6['folio'])].copy()
    n11 = n10[n10['folio'].isin(n9['folio'])].copy()
    n12 = n11.merge(n6, left_on='folio', right_on='folio', how='inner')
    n13 = n12.groupby(['ent'], as_index=False).agg(avg_seeds_expense=('su234', 'mean'))
    n14 = n13.sort_values('avg_seeds_expense', ascending=False)
    n15 = n14.head(5)

    return n15