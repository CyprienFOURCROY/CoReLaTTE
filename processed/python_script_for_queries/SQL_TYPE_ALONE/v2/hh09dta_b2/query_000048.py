import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n4 = tables['ii_ah'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(min_ah03m=('ah03m', 'min'))
    n6 = n5[(n5['min_ah03m'] == 1)].copy()
    n7 = tables['ii_inr'].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(min_inr02a=('inr02a', 'min'))
    n9 = n8[(n8['min_inr02a'] == 1)].copy()
    n10 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n11 = n10.merge(n9, left_on='folio', right_on='folio', how='left')
    n12 = n11.groupby(['ent'], as_index=False).agg(n_households_adult_poultry=('ent', 'count'), n_households_sold_dairy=('min_inr02a', 'count'))
    n13 = n12.sort_values('ent', ascending=True)

    return n13