import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01d'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_ah'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(household_electronics_value=('ah04e_2', 'max'))
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = tables['ii_portad'].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_electronics_value=('household_electronics_value', 'mean'), num_households=('folio', 'count'))
    n11 = pd.DataFrame({'overall_avg_electronics_value': [n6['household_electronics_value'].mean()]})
    n11_overall_avg_electronics_value_value = n11['overall_avg_electronics_value'].iloc[0]
    n12 = n10[n10['avg_electronics_value'] >= n11_overall_avg_electronics_value_value].copy()
    n13 = n12.sort_values('avg_electronics_value', ascending=False)

    return n13