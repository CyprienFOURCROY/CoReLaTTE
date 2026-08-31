import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1)].copy()
    n3 = tables['ii_se'].copy()
    n4 = n3[(n3['se01e'] == 3)].copy()
    n5 = n2.merge(n4, left_on='folio', right_on='folio', how='inner')
    n6 = pd.DataFrame({'avg_seed_no_loss': [n5['su234'].mean()]})
    n6_avg_seed_no_loss_value = n6['avg_seed_no_loss'].iloc[0]
    n7 = n2[n2['su234'] > n6_avg_seed_no_loss_value].copy()
    n8 = n7[['folio', 'su234']].copy()
    n9 = n8.sort_values('su234', ascending=False)

    return n9