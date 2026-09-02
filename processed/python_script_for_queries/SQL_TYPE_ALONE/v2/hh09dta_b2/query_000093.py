import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0) & (n1['edad'] >= 70.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(n70plus=('folio', 'count'))
    n5 = tables['ii_in'].copy()
    n6 = n4.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6[(n6['in01a10_1'] == 1.0)].copy()
    n8 = tables['ii_crh'].copy()
    n9 = n8[(n8['crh03_1'] == 1.0)].copy()
    n10 = n9[['folio']].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(n_pay=('folio', 'count'))
    n12 = n7[n7['folio_x'].isin(n11['folio'])].copy()
    n13 = n12.merge(n8, left_on='folio_x', right_on='folio', how='inner')
    n14 = n13[(n13['crh04_1'] == 1.0) & (n13['crh04_2'] > 0.0)].copy()
    n15 = pd.DataFrame({'avg_debt': [n14['crh04_2'].mean()]})
    n15_avg_debt_value = n15['avg_debt'].iloc[0]
    n16 = n14[n14['crh04_2'] > n15_avg_debt_value].copy()
    n17 = n16[['folio_x', 'crh04_2']].copy()
    n18 = n17.sort_values('crh04_2', ascending=False)

    return n18