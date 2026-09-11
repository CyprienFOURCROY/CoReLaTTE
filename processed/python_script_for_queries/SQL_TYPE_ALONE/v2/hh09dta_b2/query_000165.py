import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01b'] == 1)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_crh'].copy()
    n5 = n4[(n4['crh04_1'] == 1)].copy()
    n6 = n5[['folio', 'crh04_2']].copy()
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = pd.DataFrame({'overall_mean_debt': [n7['crh04_2'].mean()]})
    n8_overall_mean_debt_value = n8['overall_mean_debt'].iloc[0]
    n9 = n7[n7['crh04_2'] > n8_overall_mean_debt_value].copy()
    n10 = tables['ii_portad'].copy()
    n11 = n10[(n10['edad'] >= 18)].copy()
    n12 = n11.groupby(['folio'], as_index=False).agg(adult_count=('ls', 'count'))
    n13 = n9[n9['folio'].isin(n12['folio'])].copy()
    n14 = n10.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n15 = n13.merge(n14, left_on='folio', right_on='folio', how='inner')
    n16 = tables['ii_nna'].copy()
    n17 = n16[['folio', 'nna01']].copy()
    n18 = n15.merge(n17, left_on='folio', right_on='folio', how='inner')
    n19 = n18.groupby(['ent', 'nna01'], as_index=False).agg(avg_debt_above_overall_mean=('crh04_2', 'mean'), household_count=('folio', 'count'))

    return n19