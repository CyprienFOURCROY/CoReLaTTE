import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03e'] == 1.0) & (n1['ah04e_1'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(hh_device_value=('ah04e_2', 'max'))
    n4 = tables['ii_portad'].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n6 = n3.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6.groupby(['ent'], as_index=False).agg(state_avg_value=('hh_device_value', 'mean'), n_households=('folio', 'count'))
    n8 = n7[(n7['n_households'] >= 30)].copy()
    n9 = pd.DataFrame({'overall_avg_value': [n6['hh_device_value'].mean()]})
    n9_overall_avg_value_value = n9['overall_avg_value'].iloc[0]
    n10 = n8[n8['state_avg_value'] > n9_overall_avg_value_value].copy()
    n11 = n10[['ent', 'n_households', 'state_avg_value']].copy()

    return n11