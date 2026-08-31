import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18.0) & (n1['edad'] <= 24.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(youth_count=('edad', 'count'))
    n4 = n1.groupby(['folio'], as_index=False).agg(avg_age=('edad', 'mean'), ent=('ent', 'max'))
    n5 = pd.DataFrame({'global_avg_age': [n4['avg_age'].mean()]})
    n5_global_avg_age_value = n5['global_avg_age'].iloc[0]
    n6 = n4[n4['avg_age'] >= n5_global_avg_age_value].copy()
    n7 = n6[n6['folio'].isin(n3['folio'])].copy()
    n8 = tables['ii_su'].copy()
    n9 = n8[(n8['su01'] == 1.0)].copy()
    n10 = n7[n7['folio'].isin(n9['folio'])].copy()
    n11 = tables['ii_nna'].copy()
    n12 = n10.merge(n11, left_on='folio', right_on='folio', how='left')
    n13 = n12.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n14 = n12[(n12['nna01'] == 1.0)].copy()
    n15 = n14.groupby(['ent'], as_index=False).agg(n_with_business=('folio', 'count'))
    n16 = n13.merge(n15, left_on='ent', right_on='ent', how='left')

    return n16