import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = tables['ii_nna'].copy()
    n3 = n2[(n2['nna01'] == 1.0)].copy()
    n4 = n1[n1['folio'].isin(n3['folio'])].copy()
    n5 = n2[(n2['nna01'] == 2.0)].copy()
    n6 = n1[n1['folio'].isin(n5['folio'])].copy()
    n7 = pd.DataFrame({'avg_age_no_business': [n6['edad'].mean()]})
    n7_avg_age_no_business_value = n7['avg_age_no_business'].iloc[0]
    n8 = n4[n4['edad'] > n7_avg_age_no_business_value].copy()
    n9 = n8[['folio', 'ls', 'edad']].copy()

    return n9