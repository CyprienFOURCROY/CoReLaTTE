import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['ent'] == 20.0)].copy()
    n3 = tables['ii_nna'].copy()
    n4 = n2.merge(n3, left_on='folio', right_on='folio', how='inner')
    n5 = n4[(n4['nna01'] == 1.0)].copy()
    n6 = n4[(n4['nna01'] == 2.0)].copy()
    n7 = pd.DataFrame({'avg_age_no_business_oax': [n6['edad'].mean()]})
    n7_avg_age_no_business_oax_value = n7['avg_age_no_business_oax'].iloc[0]
    n8 = n5[n5['edad'] >= n7_avg_age_no_business_oax_value].copy()
    n9 = n8[['folio', 'ls', 'edad']].copy()

    return n9