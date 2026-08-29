import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01b'] == 1)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_ah'].copy()
    n5 = n4[['folio', 'ah04e_2']].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6[['folio', 'ent']].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8[n8['folio'].isin(n3['folio'])].copy()
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_electronic_value=('ah04e_2', 'mean'), respondent_count=('folio', 'count'))
    n11 = n10[(n10['respondent_count'] >= 2)].copy()
    n12 = n11.sort_values('avg_electronic_value', ascending=False)
    n13 = n12.head(10)

    return n13