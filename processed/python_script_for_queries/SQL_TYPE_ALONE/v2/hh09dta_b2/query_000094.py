import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20)].copy()
    n3 = pd.DataFrame({'oaxaca_mean_age': [n2['edad'].mean()]})
    n4 = tables['ii_vlh'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(ent=('vlh10a', 'max'))
    n6 = tables['ii_se'].copy()
    n7 = n1.merge(n5, left_on='folio', right_on='folio', how='inner')
    n8 = n7.merge(n6, left_on='folio', right_on='folio', how='inner')
    n9 = n8[(n8['ent_x'] == 20) & (n8['ent_y'] == 1) & (n8['se01a'] == 3)].copy()
    n3_oaxaca_mean_age_value = n3['oaxaca_mean_age'].iloc[0]
    n10 = n9[n9['edad'] > n3_oaxaca_mean_age_value].copy()
    n11 = pd.DataFrame({'n_individuals': [n10['folio'].count()]})

    return n11