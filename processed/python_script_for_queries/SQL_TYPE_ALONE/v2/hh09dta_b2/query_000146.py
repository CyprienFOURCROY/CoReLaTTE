import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03d'] == 1)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(owners=('ah03d', 'count'))
    n4 = tables['ii_vlh'].copy()
    n5 = n4[n4['folio'].isin(n3['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.groupby(['ent'], as_index=False).agg(avg_safety=('vlh04', 'mean'), hh_count=('vlh04', 'count'))
    n10 = n9[(n9['hh_count'] >= 30)].copy()
    n11 = pd.DataFrame({'overall_avg_safety': [n8['vlh04'].mean()]})
    n11_overall_avg_safety_value = n11['overall_avg_safety'].iloc[0]
    n12 = n10[n10['avg_safety'] > n11_overall_avg_safety_value].copy()
    n13 = n12[['ent', 'avg_safety', 'hh_count']].copy()
    n14 = n13.sort_values('avg_safety', ascending=False)

    return n14