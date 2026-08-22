import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(avg_age_hh=('edad', 'mean'), ent=('ent', 'max'))
    n3 = tables['ii_in'].copy()
    n4 = n3[(n3['in02a10'] > 0)].copy()
    n5 = tables['ii_su'].copy()
    n6 = n5[(n5['su01'] == 1)].copy()
    n7 = n4[n4['folio'].isin(n6['folio'])].copy()
    n8 = n2.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(state_avg_age=('avg_age_hh', 'mean'), n_households=('avg_age_hh', 'count'))
    n10 = n9.sort_values('state_avg_age', ascending=False)
    n11 = n10.head(10)

    return n11