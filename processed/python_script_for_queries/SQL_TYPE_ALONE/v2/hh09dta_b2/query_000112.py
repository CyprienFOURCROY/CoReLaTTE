import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh02_1'] == 1) & (n1['crh03_1'] == 1)].copy()
    n3 = tables['ii_ah'].copy()
    n4 = n3[(n3['ah03e'] == 1)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = tables['ii_portad'].copy()
    n7 = n6[(n6['ent'] == 20)].copy()
    n8 = n5[n5['folio'].isin(n7['folio'])].copy()
    n9 = pd.DataFrame({'avg_paid': [n8['crh03_2'].mean()]})
    n9_avg_paid_value = n9['avg_paid'].iloc[0]
    n10 = n8[n8['crh03_2'] > n9_avg_paid_value].copy()
    n11 = n10[['folio', 'crh03_2']].copy()
    n12 = n11.sort_values('crh03_2', ascending=False)

    return n12