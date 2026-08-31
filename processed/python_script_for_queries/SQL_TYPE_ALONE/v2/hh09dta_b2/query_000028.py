import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = pd.DataFrame({'avg_age': [n1['edad'].mean()]})
    n2_avg_age_value = n2['avg_age'].iloc[0]
    n3 = n1[n1['edad'] > n2_avg_age_value].copy()
    n4 = n3[(n3['edad'] >= 18)].copy()
    n5 = tables['ii_se'].copy()
    n6 = n4.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6[(n6['se01e'] == 1)].copy()
    n8 = tables['ii_su'].copy()
    n9 = n7.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9[(n9['su01'] == 1)].copy()
    n11 = tables['ii_nna'].copy()
    n12 = n11[(n11['nna01'] == 1)].copy()
    n13 = n10[n10['folio'].isin(n12['folio'])].copy()
    n14 = n13.groupby(['ent'], as_index=False).agg(n_people=('ls', 'count'), avg_seed_expense=('su234', 'mean'))

    return n14