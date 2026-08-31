import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n3[(n3['inr02c'] == 1.0)].copy()
    n5 = n4[['folio', 'inr02c']].copy()
    n6 = n2.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = tables['ii_in'].copy()
    n8 = n7[['folio', 'in02a10']].copy()
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['folio'], as_index=False).agg(hh_in02a10=('in02a10', 'mean'))
    n11 = pd.DataFrame({'oax_mean_in02a10': [n10['hh_in02a10'].mean()]})
    n11_oax_mean_in02a10_value = n11['oax_mean_in02a10'].iloc[0]
    n12 = n9[n9['in02a10'] > n11_oax_mean_in02a10_value].copy()
    n13 = pd.DataFrame({'mean_edad_oax_meat': [n6['edad'].mean()]})
    n13_mean_edad_oax_meat_value = n13['mean_edad_oax_meat'].iloc[0]
    n14 = n12[n12['edad'] >= n13_mean_edad_oax_meat_value].copy()
    n15 = n14[['folio', 'ls', 'edad', 'in02a10']].copy()
    n16 = n15.sort_values('edad', ascending=False)
    n17 = n16.head(10)

    return n17