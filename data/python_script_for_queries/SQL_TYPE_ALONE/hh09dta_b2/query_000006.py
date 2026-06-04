import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_in'].copy()
    n2 = n1[(n1['in01a10_1'] == 1.0) & (n1['in03a'] == 1.0) & (n1['in02a10'] > 0)].copy()
    n3 = n2[['folio', 'in02a10', 'in03a']].copy()
    n4 = tables['ii_portad'].copy()
    n5 = n4[['folio', 'ent']].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n7 = n3.merge(n6, left_on='folio', right_on='folio', how='inner')
    n11 = tables['ii_su'].copy()
    n12 = n11[(n11['su01'] == 1.0)].copy()
    n13 = n12[['folio']].copy()
    n14 = n7[n7['folio'].isin(n13['folio'])].copy()
    n8 = n14.groupby(['ent'], as_index=False).agg(avg_in02a10=('in02a10', 'mean'), household_count=('folio', 'count'))
    n15 = n8.sort_values('avg_in02a10', ascending=False)
    n16 = n15.head(10)

    return n16