import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh16a'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = n5.groupby(['ent'], as_index=False).agg(avg_age_yes=('edad', 'mean'), n_yes=('edad', 'count'))
    n7 = n1[(n1['vlh16a'] == 3.0)].copy()
    n8 = n7[['folio']].copy()
    n9 = n4[n4['folio'].isin(n8['folio'])].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_age_no=('edad', 'mean'), n_no=('edad', 'count'))
    n11 = n6.merge(n10, left_on='ent', right_on='ent', how='outer')
    n12 = n11.sort_values('avg_age_yes', ascending=False)
    n13 = n12.head(10)

    return n13