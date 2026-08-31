import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[['folio', 'ent']].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n3[['folio', 'ah03d']].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5[(n5['ah03d'] == 1.0)].copy()
    n7 = tables['ii_crh'].copy()
    n8 = n6.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8[(n8['crh04_1'] == 1.0)].copy()
    n10 = n9.groupby(['folio', 'ent'], as_index=False).agg(hh_debt=('crh04_2', 'max'))
    n11 = pd.DataFrame({'global_avg_debt': [n10['hh_debt'].mean()]})
    n11_global_avg_debt_value = n11['global_avg_debt'].iloc[0]
    n12 = n10[n10['hh_debt'] > n11_global_avg_debt_value].copy()
    n13 = n12.groupby(['ent'], as_index=False).agg(n_households_above_avg=('folio', 'count'))
    n14 = n13.sort_values('n_households_above_avg', ascending=False)

    return n14