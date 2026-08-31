import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1) & (n1['su234'] > 0)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n3[(n3['ah03d'] == 1)].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(cnt_veh_yes=('ah03d', 'count'))
    n6 = n2[n2['folio'].isin(n5['folio'])].copy()
    n7 = pd.DataFrame({'avg_seed_exp': [n2['su234'].mean()]})
    n7_avg_seed_exp_value = n7['avg_seed_exp'].iloc[0]
    n8 = n6[n6['su234'] > n7_avg_seed_exp_value].copy()
    n9 = n8[['folio', 'su234']].copy()
    n10 = n9.sort_values('su234', ascending=False)

    return n10