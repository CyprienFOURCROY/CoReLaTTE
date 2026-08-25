import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = pd.DataFrame({'avg_age': [n1['edad'].mean()]})
    n2_avg_age_value = n2['avg_age'].iloc[0]
    n3 = n1[n1['edad'] > n2_avg_age_value].copy()
    n4 = tables['ii_crh'].copy()
    n5 = n4[(n4['crh04_1'] == 1) & (n4['crh04_2'] > 0)].copy()
    n6 = n3[n3['folio'].isin(n5['folio'])].copy()
    n7 = n6.merge(n5, left_on='folio', right_on='folio', how='inner')
    n8 = n7.groupby(['ent'], as_index=False).agg(avg_debt=('crh04_2', 'mean'), num_individuals=('folio', 'count'))
    n9 = n8.sort_values('avg_debt', ascending=False)
    n10 = n9.head(5)

    return n10