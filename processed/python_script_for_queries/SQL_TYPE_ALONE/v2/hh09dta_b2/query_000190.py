import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(avg_age=('edad', 'mean'))
    n4 = tables['ii_in'].copy()
    n5 = n4[(n4['in03a'] == 1.0)].copy()
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = tables['ii_ah'].copy()
    n8 = n7[n7['folio'].isin(n3['folio'])].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(total_electronics_value=('ah04e_2', 'sum'))
    n10 = n3.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = n10.merge(n6, left_on='folio', right_on='folio', how='inner')
    n12 = pd.DataFrame({'overall_oax_avg_age': [n3['avg_age'].mean()]})
    n12_overall_oax_avg_age_value = n12['overall_oax_avg_age'].iloc[0]
    n13 = n11[n11['avg_age'] > n12_overall_oax_avg_age_value].copy()
    n14 = pd.DataFrame({'mean_electronics_value_above': [n13['total_electronics_value'].mean()], 'num_households_above': [n13['folio'].count()]})

    return n14