import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20)].copy()
    n3 = n2[['folio']].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(hh_person_count=('folio', 'count'))
    n5 = tables['ii_su'].copy()
    n6 = n5[['folio', 'su237']].copy()
    n7 = n6[n6['folio'].isin(n4['folio'])].copy()
    n8 = pd.DataFrame({'avg_su237_oaxaca': [n7['su237'].mean()]})
    n8_avg_su237_oaxaca_value = n8['avg_su237_oaxaca'].iloc[0]
    n9 = n7[n7['su237'] > n8_avg_su237_oaxaca_value].copy()
    n10 = tables['ii_nna'].copy()
    n11 = n10[['folio', 'nna02']].copy()
    n12 = n11.groupby(['folio'], as_index=False).agg(nna02_total=('nna02', 'sum'))
    n13 = n9.merge(n12, left_on='folio', right_on='folio', how='left')
    n14 = tables['ii_vlh'].copy()
    n15 = n14[['folio', 'vlh08a']].copy()
    n16 = n15.groupby(['folio'], as_index=False).agg(vlh08a_min=('vlh08a', 'min'))
    n17 = n13.merge(n16, left_on='folio', right_on='folio', how='left')
    n18 = n17.groupby(['nna02_total', 'vlh08a_min'], as_index=False).agg(avg_su237=('su237', 'mean'), households=('folio', 'count'))

    return n18