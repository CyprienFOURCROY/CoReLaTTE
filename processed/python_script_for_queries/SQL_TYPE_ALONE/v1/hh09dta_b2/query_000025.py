import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01a'] == 1)].copy()
    n3 = tables['ii_crh'].copy()
    n4 = n3[n3['folio'].isin(n2['folio'])].copy()
    n5 = n4[(n4['crh02_1'] == 1)].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(n_households_with_debt_after_death=('folio', 'count'))
    n10 = n9.sort_values('n_households_with_debt_after_death', ascending=False)
    n11 = n10.head(10)

    return n11