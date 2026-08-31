import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh04_1'] == 1.0) & (n1['crh04_2'] > 0.0)].copy()
    n3 = tables['ii_vlh'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = tables['ii_vlh'].copy()
    n6 = n4.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6[(n6['vlh04_x'].isin([3.0, 4.0])) & (n6['vlh01k_y'].isin([3.0, 4.0]))].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(ent_min=('ent', 'min'))
    n10 = n9[(n9['ent_min'] == 20.0)].copy()
    n11 = n7[n7['folio'].isin(n10['folio'])].copy()
    n12 = pd.DataFrame({'avg_debt_oax_unsafe_disagree': [n11['crh04_2'].mean()], 'n_households': [n11['crh04_2'].count()]})

    return n12