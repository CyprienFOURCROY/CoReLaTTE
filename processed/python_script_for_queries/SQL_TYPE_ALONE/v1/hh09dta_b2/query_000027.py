import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio', 'ent'], as_index=False).agg(avg_age=('edad', 'mean'))
    n3 = tables['ii_nna'].copy()
    n4 = n3[(n3['nna01'] == 1.0)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = n5.groupby(['ent'], as_index=False).agg(avg_household_age=('avg_age', 'mean'), households=('folio', 'count'))
    n7 = n6.sort_values('avg_household_age', ascending=False)

    return n7