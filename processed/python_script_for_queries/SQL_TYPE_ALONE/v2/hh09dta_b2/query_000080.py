import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n4 = tables['ii_ah'].copy()
    n5 = n4[(n4['ah04e_1'] == 1) & (n4['ah04e_2'] > 0)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(hh_elec_value=('ah04e_2', 'max'))
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = tables['ii_se'].copy()
    n9 = n8[(n8['se01a'] == 1)].copy()
    n10 = n7.merge(n9, left_on='folio', right_on='folio', how='inner')
    n11 = pd.DataFrame({'avg_elec_value_shock': [n10['hh_elec_value'].mean()]})
    n12 = pd.DataFrame({'avg_elec_value_overall': [n7['hh_elec_value'].mean()]})
    n12_avg_elec_value_overall_value = n12['avg_elec_value_overall'].iloc[0]
    n13 = n11[n11['avg_elec_value_shock'] > n12_avg_elec_value_overall_value].copy()

    return n13