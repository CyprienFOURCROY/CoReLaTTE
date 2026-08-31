import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_vlh'].copy()
    n2 = n1[(n1['vlh18a'] == 0) & (n1['vlh10a'] == 1)].copy()
    n3 = n2[['folio', 'vlh18a', 'vlh10a']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n3.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = pd.DataFrame({'avg_edad': [n5['edad'].mean()]})
    n6_avg_edad_value = n6['avg_edad'].iloc[0]
    n7 = n5[n5['edad'] > n6_avg_edad_value].copy()
    n8 = n7[['folio', 'ent', 'edad', 'vlh18a']].copy()
    n9 = n8.sort_values('edad', ascending=False)

    return n9