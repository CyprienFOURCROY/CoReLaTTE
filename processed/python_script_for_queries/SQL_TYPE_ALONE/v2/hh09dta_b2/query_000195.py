import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(max_edad=('edad', 'max'))
    n4 = n3[(n3['max_edad'] >= 65)].copy()
    n5 = tables['ii_se'].copy()
    n6 = n5[(n5['se01a'] == 1)].copy()
    n8 = tables['ii_crh'].copy()
    n9 = n8[(n8['crh04_1'] == 1)].copy()
    n10 = n4.merge(n6, left_on='folio', right_on='folio', how='inner')
    n11 = n10.merge(n9, left_on='folio', right_on='folio', how='inner')
    n13 = n3.merge(n9, left_on='folio', right_on='folio', how='inner')
    n14 = pd.DataFrame({'oax_mean_debt': [n13['crh04_2'].mean()]})
    n14_oax_mean_debt_value = n14['oax_mean_debt'].iloc[0]
    n15 = n11[n11['crh04_2'] > n14_oax_mean_debt_value].copy()
    n16 = pd.DataFrame({'n_households_above_oax_mean_debt': [n15['folio'].count()]})

    return n16