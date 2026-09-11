import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'), n_adults=('folio', 'count'))
    n4 = tables['ii_inr'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_se'].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['inr02c'] == 1) & (n7['se01b'] == 1)].copy()
    n9 = n8.groupby(['ent'], as_index=False).agg(qualified_hh=('folio', 'count'))
    n10 = pd.DataFrame({'avg_qualified_hh': [n9['qualified_hh'].mean()]})
    n10_avg_qualified_hh_value = n10['avg_qualified_hh'].iloc[0]
    n11 = n9[n9['qualified_hh'] >= n10_avg_qualified_hh_value].copy()
    n12 = n11[['ent', 'qualified_hh']].copy()

    return n12