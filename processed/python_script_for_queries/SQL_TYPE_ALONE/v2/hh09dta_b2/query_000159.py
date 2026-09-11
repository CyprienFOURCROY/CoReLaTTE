import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_inr'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3[['folio', 'edad', 'inr02a', 'ls_x', 'ls_y']].copy()
    n5 = n4[(n4['inr02a'].isin([1.0, 3.0]))].copy()
    n6 = tables['ii_crh'].copy()
    n7 = n6[(n6['crh04_1'] == 1.0)].copy()
    n8 = n5[n5['folio'].isin(n7['folio'])].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(oldest_age=('edad', 'max'), inr02a_status=('inr02a', 'max'))
    n10 = n9.merge(n7, left_on='folio', right_on='folio', how='inner')
    n11 = pd.DataFrame({'mean_oldest_age': [n10['oldest_age'].mean()]})
    n11_mean_oldest_age_value = n11['mean_oldest_age'].iloc[0]
    n12 = n10[n10['oldest_age'] >= n11_mean_oldest_age_value].copy()
    n13 = n12.groupby(['inr02a_status'], as_index=False).agg(n_households=('folio', 'count'))
    n14 = n13.sort_values('inr02a_status', ascending=True)

    return n14