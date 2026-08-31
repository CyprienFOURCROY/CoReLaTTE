import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(n_people=('ls', 'count'))
    n3 = tables['ii_ah'].copy()
    n4 = n3[(n3['ah04e_1'] == 1.0) & (n3['ah04e_2'] > 0.0)].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(n_elec_records=('ah04e_2', 'count'))
    n6 = n2[n2['folio'].isin(n5['folio'])].copy()
    n7 = pd.DataFrame({'avg_people': [n6['n_people'].mean()]})

    return n7