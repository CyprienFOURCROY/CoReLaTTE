import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in02a10'] > 0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4[(n4['edad'] >= 60)].copy()
    n6 = tables['ii_ah'].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['ah03e'] == 1.0) & (n7['ah04e_1'] == 1.0) & (n7['ah04e_2'] > 0)].copy()
    n9 = n8[['folio', 'ent', 'ah04e_2', 'ls_x']].copy()
    n10 = n9.groupby(['folio', 'ent'], as_index=False).agg(hh_max_e_device_value=('ah04e_2', 'max'), n_rows=('ls_x', 'count'))
    n11 = n10[n10['folio'].isin(n3['folio'])].copy()
    n12 = n11.groupby(['ent'], as_index=False).agg(avg_hh_max_e_device_value=('hh_max_e_device_value', 'mean'), n_households=('folio', 'count'))
    n13 = n12.sort_values('ent', ascending=True)

    return n13