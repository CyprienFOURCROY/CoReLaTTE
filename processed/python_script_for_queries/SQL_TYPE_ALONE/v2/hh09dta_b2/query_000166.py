import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh10a'] == 3.0)].copy()
    n3 = tables['ii_portad'].copy()
    n4 = n3.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = n5.groupby(['ent'], as_index=False).agg(avg_vlh04=('vlh04', 'mean'), n_households=('folio', 'count'))
    n7 = n6[(n6['avg_vlh04'] >= 3.0)].copy()
    n8 = pd.DataFrame({'national_avg_vlh04': [n5['vlh04'].mean()]})
    n8_national_avg_vlh04_value = n8['national_avg_vlh04'].iloc[0]
    n9 = n7[n7['avg_vlh04'] > n8_national_avg_vlh04_value].copy()
    n10 = n9.sort_values('avg_vlh04', ascending=False)
    n11 = n10[['ent', 'avg_vlh04', 'n_households']].copy()

    return n11