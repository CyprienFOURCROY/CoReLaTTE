import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03e'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(device_members=('ls', 'count'))
    n4 = tables['ii_in'].copy()
    n5 = n4[(n4['in01a10_1'] == 1.0) & (n4['in02a10'] > 0.0)].copy()
    n6 = n5[n5['folio'].isin(n3['folio'])].copy()
    n7 = tables['ii_portad'].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['ent'], as_index=False).agg(avg_other_gov_income=('in02a10', 'mean'), n_households=('folio', 'count'))
    n11 = n10[(n10['n_households'] >= 30) & (n10['avg_other_gov_income'] > 2000.0)].copy()
    n12 = n11.sort_values('avg_other_gov_income', ascending=False)

    return n12