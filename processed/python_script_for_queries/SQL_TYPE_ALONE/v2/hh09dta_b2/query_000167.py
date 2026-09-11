import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in03a'] == 1.0)].copy()
    n3 = tables['ii_portad'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = pd.DataFrame({'avg_edad': [n4['edad'].mean()]})
    n6 = tables['ii_vlh'].copy()
    n7 = n4.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7[(n7['vlh04'].isin([3.0, 4.0]))].copy()
    n9 = n8[['folio', 'edad', 'vlh04']].copy()
    n5_avg_edad_value = n5['avg_edad'].iloc[0]
    n10 = n9[n9['edad'] > n5_avg_edad_value].copy()

    return n10