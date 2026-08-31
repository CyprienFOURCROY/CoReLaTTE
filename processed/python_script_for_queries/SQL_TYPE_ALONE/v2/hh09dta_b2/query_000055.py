import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah04f_1'] == 1.0)].copy()
    n3 = n2[['folio', 'ah04f_2']].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(wash_value=('ah04f_2', 'sum'))
    n5 = tables['ii_nna'].copy()
    n6 = n5[(n5['nna01'] == 1.0)].copy()
    n7 = n6[['folio']].copy()
    n8 = tables['ii_crh'].copy()
    n9 = n8[(n8['crh02_1'] == 2.0)].copy()
    n10 = n9[['folio']].copy()
    n11 = tables['ii_portad'].copy()
    n12 = n11[(n11['edad'] >= 18.0)].copy()
    n13 = n12[['folio', 'ent']].copy()
    n14 = n13.groupby(['folio', 'ent'], as_index=False).agg(hh_rows=('folio', 'count'))
    n15 = n4[n4['folio'].isin(n7['folio'])].copy()
    n16 = n15[n15['folio'].isin(n10['folio'])].copy()
    n17 = n16.merge(n14, left_on='folio', right_on='folio', how='inner')
    n18 = n17.groupby(['ent'], as_index=False).agg(avg_wash_value=('wash_value', 'mean'))
    n19 = pd.DataFrame({'national_avg_wash_value': [n17['wash_value'].mean()]})
    n19_national_avg_wash_value_value = n19['national_avg_wash_value'].iloc[0]
    n20 = n18[n18['avg_wash_value'] > n19_national_avg_wash_value_value].copy()
    n21 = n20.sort_values('avg_wash_value', ascending=False)

    return n21