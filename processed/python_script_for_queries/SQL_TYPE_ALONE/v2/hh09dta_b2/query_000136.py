import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in02a10'] > 0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(n_records=('folio', 'count'))
    n4 = tables['ii_inr'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent_min=('ent', 'min'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent_min'], as_index=False).agg(n_hh_qualifying=('folio', 'count'))
    n10 = n9[(n9['n_hh_qualifying'] >= 30)].copy()
    n11 = n8[n8['ent_min'].isin(n10['ent_min'])].copy()
    n12 = n11[(n11['inr02a'] == 1)].copy()
    n13 = n12.groupby(['ent_min'], as_index=False).agg(n_dairy_yes=('folio', 'count'))
    n14 = n10.merge(n13, left_on='ent_min', right_on='ent_min', how='left')

    return n14