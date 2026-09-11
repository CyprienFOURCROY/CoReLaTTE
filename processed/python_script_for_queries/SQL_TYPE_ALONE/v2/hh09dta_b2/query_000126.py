import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1.0)].copy()
    n3 = tables['ii_inr'].copy()
    n4 = n3[(n3['inr02c'] == 1.0) & (n3['inr02d'] == 1.0)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6[n6['folio'].isin(n5['folio'])].copy()
    n8 = pd.DataFrame({'overall_avg_age': [n7['edad'].mean()]})
    n9 = n7.groupby(['ent'], as_index=False).agg(state_avg_age=('edad', 'mean'), n_individuals=('edad', 'count'))
    n10 = n9[(n9['n_individuals'] >= 30)].copy()
    n8_overall_avg_age_value = n8['overall_avg_age'].iloc[0]
    n11 = n10[n10['state_avg_age'] > n8_overall_avg_age_value].copy()
    n12 = n11[['ent', 'state_avg_age', 'n_individuals']].copy()
    n13 = n12.sort_values('state_avg_age', ascending=False)

    return n13