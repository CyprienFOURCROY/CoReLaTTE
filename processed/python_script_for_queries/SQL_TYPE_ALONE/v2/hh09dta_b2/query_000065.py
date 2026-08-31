import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03e'] == 1) & (n1['ah03f'] == 1)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(members_with_both=('ls', 'count'))
    n4 = tables['ii_nna'].copy()
    n5 = n4[(n4['nna01'] == 1)].copy()
    n6 = n3.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6[['folio']].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8[(n8['edad'] >= 18)].copy()
    n10 = n9[n9['folio'].isin(n7['folio'])].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(avg_adult_age_in_qual_hh=('edad', 'mean'), adult_count=('ls', 'count'))
    n12 = n11.sort_values('avg_adult_age_in_qual_hh', ascending=False)
    n13 = n12.head(10)

    return n13