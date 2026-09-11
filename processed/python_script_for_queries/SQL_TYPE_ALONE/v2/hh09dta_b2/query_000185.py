import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(oldest_age=('edad', 'max'), ent=('ent', 'max'))
    n3 = n2[(n2['ent'] == 20.0)].copy()
    n4 = n1[(n1['edad'] >= 18)].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(adult_count=('folio', 'count'))
    n6 = n3[n3['folio'].isin(n5['folio'])].copy()
    n7 = tables['ii_inr'].copy()
    n8 = n7[(n7['inr02d'] == 1.0)].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(egg_rows=('folio', 'count'))
    n10 = n6[n6['folio'].isin(n9['folio'])].copy()
    n11 = pd.DataFrame({'avg_oldest_age': [n10['oldest_age'].mean()]})

    return n11