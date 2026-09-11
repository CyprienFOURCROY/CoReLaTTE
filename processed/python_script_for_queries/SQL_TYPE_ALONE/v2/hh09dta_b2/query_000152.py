import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_su'].copy()
    n3 = n2[(n2['su01'] == 1)].copy()
    n4 = n1[n1['folio'].isin(n3['folio'])].copy()
    n5 = pd.DataFrame({'overall_subset_avg_age': [n4['edad'].mean()]})
    n5_overall_subset_avg_age_value = n5['overall_subset_avg_age'].iloc[0]
    n6 = n4[n4['edad'] > n5_overall_subset_avg_age_value].copy()
    n7 = n6.groupby(['ent'], as_index=False).agg(num_individuals_older_than_subset_avg=('edad', 'count'), avg_age_of_older_than_subset_avg=('edad', 'mean'))

    return n7