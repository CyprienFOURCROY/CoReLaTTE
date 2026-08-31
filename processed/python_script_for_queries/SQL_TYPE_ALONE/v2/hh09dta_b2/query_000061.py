import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n3[(n3['inr02i'] == 3)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_portad'].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7.groupby(['ent', 'folio'], as_index=False).agg(rows_per_hh=('folio', 'count'))
    n9 = n8.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n10 = n9[(n9['n_households'] >= 40)].copy()
    n11 = n7.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'))
    n12 = n11.merge(n10, left_on='ent', right_on='ent', how='inner')
    n13 = pd.DataFrame({'overall_avg_age': [n6['edad'].mean()]})
    n13_overall_avg_age_value = n13['overall_avg_age'].iloc[0]
    n14 = n12[n12['avg_age'] < n13_overall_avg_age_value].copy()
    n15 = n14[['ent', 'n_households', 'avg_age']].copy()
    n16 = n15.sort_values('avg_age', ascending=True)

    return n16