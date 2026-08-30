import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_vlh'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = tables['ii_su'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[(n5['edad'] >= 18) & (n5['vlh07b'] == 1) & (n5['su01'] == 1)].copy()
    n7 = n6.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'), n_adults=('edad', 'count'))
    n8 = n7.sort_values('avg_age', ascending=False)
    n9 = n8.head(5)

    return n9