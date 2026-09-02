import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['ent'], as_index=False).agg(avg_age=('edad', 'mean'))
    n3 = pd.DataFrame({'overall_avg_age': [n1['edad'].mean()]})
    n3_overall_avg_age_value = n3['overall_avg_age'].iloc[0]
    n4 = n2[n2['avg_age'] > n3_overall_avg_age_value].copy()
    n5 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n6 = n5[n5['ent'].isin(n4['ent'])].copy()
    n7 = tables['ii_se'].copy()
    n8 = n7[(n7['se01e'] == 1.0)].copy()
    n9 = n8[['folio']].copy()
    n10 = tables['ii_nna'].copy()
    n11 = n10[(n10['nna01'] == 1.0)].copy()
    n12 = n11[['folio']].copy()
    n13 = n9[n9['folio'].isin(n12['folio'])].copy()
    n14 = n13[n13['folio'].isin(n6['folio'])].copy()
    n15 = pd.DataFrame({'n_households': [n14['folio'].count()]})

    return n15