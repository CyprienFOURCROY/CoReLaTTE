import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(hh_count=('folio', 'count'))
    n4 = n3[['folio']].copy()
    n5 = tables['ii_crh'].copy()
    n6 = n5[n5['folio'].isin(n4['folio'])].copy()
    n7 = n6[(n6['crh04_1'] == 1.0)].copy()
    n8 = tables['ii_vlh'].copy()
    n9 = n8[n8['folio'].isin(n4['folio'])].copy()
    n10 = n9[(n9['vlh04'].isin([3.0, 4.0]))].copy()
    n11 = n10.merge(n5, left_on='folio', right_on='folio', how='inner')
    n12 = n11[(n11['crh04_1'] == 1.0)].copy()
    n13 = pd.DataFrame({'avg_debt_unsafe_oaxaca': [n12['crh04_2'].mean()]})
    n13_avg_debt_unsafe_oaxaca_value = n13['avg_debt_unsafe_oaxaca'].iloc[0]
    n14 = n7[n7['crh04_2'] > n13_avg_debt_unsafe_oaxaca_value].copy()
    n15 = n14[['folio', 'crh04_2']].copy()
    n16 = n15.sort_values('crh04_2', ascending=False)

    return n16