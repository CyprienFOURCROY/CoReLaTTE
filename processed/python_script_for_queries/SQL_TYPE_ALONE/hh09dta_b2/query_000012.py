import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in03a'] == 1) & (n1['in02a10'] > 0)].copy()
    n3 = n2[['folio', 'in02a10', 'in03a']].copy()
    n6 = tables['ii_inr'].copy()
    n7 = n6[(n6['inr02a'] == 1)].copy()
    n8 = n7[['folio']].copy()
    n9 = n3[n3['folio'].isin(n8['folio'])].copy()
    n10 = tables['ii_portad'].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(avg_edad=('edad', 'mean'))
    n12 = n9.merge(n11, left_on='folio', right_on='folio', how='left')
    n13 = n12.sort_values('in02a10', ascending=False)
    n14 = n13.head(10)

    return n14