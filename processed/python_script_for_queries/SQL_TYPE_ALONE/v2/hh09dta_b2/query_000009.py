import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 25) & (n1['ent'].isin([20, 21]))].copy()
    n3 = n2[['folio', 'ent', 'edad']].copy()
    n4 = tables['ii_vlh'].copy()
    n5 = n4[(n4['vlh04'].isin([1, 2, 3, 4]))].copy()
    n6 = n5[['folio', 'vlh04']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_crh'].copy()
    n9 = n8[(n8['crh04_1'] == 1) & (n8['crh04_2'] >= 5000)].copy()
    n10 = n9[['folio', 'crh04_2']].copy()
    n11 = n7.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11.merge(n6, left_on='folio', right_on='folio', how='inner')
    n13 = n12.groupby(['ent'], as_index=False).agg(avg_home_safety=('vlh04', 'mean'), households=('folio', 'count'), avg_total_debt=('crh04_2', 'mean'))
    n14 = n13.sort_values('avg_home_safety', ascending=True)

    return n14