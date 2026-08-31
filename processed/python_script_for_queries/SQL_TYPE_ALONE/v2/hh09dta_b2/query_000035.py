import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20)].copy()
    n3 = n2[['folio']].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(hh_rows=('folio', 'count'))
    n5 = n4[['folio']].copy()
    n6 = tables['ii_in'].copy()
    n7 = n6[(n6['in02a10'] > 0)].copy()
    n8 = n7[n7['folio'].isin(n5['folio'])].copy()
    n9 = tables['ii_crh'].copy()
    n10 = n9[(n9['crh04_1'] == 1)].copy()
    n11 = n10[n10['folio'].isin(n5['folio'])].copy()
    n12 = pd.DataFrame({'oax_avg_debt': [n11['crh04_2'].mean()]})
    n13 = n8.merge(n11, left_on='folio', right_on='folio', how='inner')
    n12_oax_avg_debt_value = n12['oax_avg_debt'].iloc[0]
    n14 = n13[n13['crh04_2'] > n12_oax_avg_debt_value].copy()
    n15 = n14[['folio', 'crh04_2', 'in02a10']].copy()
    n16 = n15.sort_values('crh04_2', ascending=False)

    return n16