import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20)].copy()
    n3 = tables['ii_se'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = tables['ii_crh'].copy()
    n6 = n4.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = n6[['folio', 'se01b', 'crh04_1', 'crh04_2']].copy()
    n8 = n7[(n7['crh04_1'] == 1)].copy()
    n9 = n3[(n3['se01b'] == 1)].copy()
    n10 = n9[['folio']].copy()
    n11 = n8[n8['folio'].isin(n10['folio'])].copy()
    n12 = n11.groupby(['folio'], as_index=False).agg(debt_total=('crh04_2', 'max'))
    n13 = pd.DataFrame({'avg_debt_total': [n12['debt_total'].mean()]})
    n13_avg_debt_total_value = n13['avg_debt_total'].iloc[0]
    n14 = n12[n12['debt_total'] > n13_avg_debt_total_value].copy()
    n15 = pd.DataFrame({'num_households_above_avg': [n14['folio'].count()]})

    return n15