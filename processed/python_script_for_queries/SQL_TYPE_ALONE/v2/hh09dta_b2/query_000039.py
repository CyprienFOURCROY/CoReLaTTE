import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_inr'].copy()
    n2 = n1[(n1['inr02a'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_inr02a=('folio', 'count'))
    n4 = tables['ii_portad'].copy()
    n5 = n4[(n4['ent'] == 20.0)].copy()
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = n6.merge(n1, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['ls_x'] == '01') & (n7['ls_y'] == 1.0)].copy()
    n9 = n8.groupby(['folio', 'ls_x'], as_index=False).agg(edad_mean=('edad', 'mean'))
    n10 = pd.DataFrame({'avg_age_ls1': [n9['edad_mean'].mean()]})

    return n10