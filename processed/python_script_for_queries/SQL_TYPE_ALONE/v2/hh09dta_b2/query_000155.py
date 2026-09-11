import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[(n1['ah03d'] == 1)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(mv_members=('ls', 'count'))
    n4 = n1[(n1['ah03h'] == 1)].copy()
    n5 = n4.groupby(['folio'], as_index=False).agg(fin_members=('ls', 'count'))
    n6 = n3.merge(n5, left_on='folio', right_on='folio', how='inner')
    n7 = tables['ii_portad'].copy()
    n8 = n7[(n7['ent'] == 20)].copy()
    n9 = n8.groupby(['folio'], as_index=False).agg(person_count=('ls', 'count'))
    n10 = n6[n6['folio'].isin(n9['folio'])].copy()
    n11 = tables['ii_crh'].copy()
    n12 = n11[(n11['crh04_1'] == 1)].copy()
    n13 = n10.merge(n12, left_on='folio', right_on='folio', how='inner')
    n14 = pd.DataFrame({'avg_total_debts': [n13['crh04_2'].mean()]})

    return n14