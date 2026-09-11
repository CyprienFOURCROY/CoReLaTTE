import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(max_edad=('edad', 'max'), ent=('ent', 'max'))
    n3 = n2[(n2['ent'] == 20.0) & (n2['max_edad'] >= 18.0)].copy()
    n4 = tables['ii_vlh'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = pd.DataFrame({'oaxaca_avg_vlh18a': [n5['vlh18a'].mean()]})
    n6_oaxaca_avg_vlh18a_value = n6['oaxaca_avg_vlh18a'].iloc[0]
    n7 = n5[n5['vlh18a'] >= n6_oaxaca_avg_vlh18a_value].copy()
    n8 = tables['ii_nna'].copy()
    n9 = n7.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9[(n9['nna01'] == 1.0)].copy()
    n11 = pd.DataFrame({'avg_vlh18a_business_at_or_above_state_mean': [n10['vlh18a'].mean()]})

    return n11