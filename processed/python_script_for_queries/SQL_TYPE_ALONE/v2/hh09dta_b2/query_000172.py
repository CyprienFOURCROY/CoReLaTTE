import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_inr'].copy()
    n5 = n4[(n4['inr02i'] == 1.0)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8.merge(n7, left_on='folio', right_on='folio', how='inner')
    n10 = n9[['ent', 'edad']].copy()
    n11 = n10.groupby(['ent'], as_index=False).agg(avg_age_state=('edad', 'mean'))
    n12 = pd.DataFrame({'overall_avg_age': [n10['edad'].mean()]})
    n12_overall_avg_age_value = n12['overall_avg_age'].iloc[0]
    n13 = n11[n11['avg_age_state'] > n12_overall_avg_age_value].copy()
    n14 = n13.sort_values('avg_age_state', ascending=False)
    n15 = n14[['ent', 'avg_age_state']].copy()

    return n15