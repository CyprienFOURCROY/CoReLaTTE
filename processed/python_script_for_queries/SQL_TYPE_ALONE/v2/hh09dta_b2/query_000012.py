import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1.0)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_crh'].copy()
    n5 = n4[(n4['crh04_1'] == 1.0) & (n4['crh04_2'] > 0.0)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(total_debt=('crh04_2', 'sum'))
    n7 = n6[n6['folio'].isin(n3['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8[['folio', 'ent', 'ls']].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(member_count=('ls', 'count'), ent=('ent', 'max'))
    n11 = n10.merge(n7, left_on='folio', right_on='folio', how='inner')
    n12 = n11.groupby(['ent'], as_index=False).agg(avg_household_size=('member_count', 'mean'), avg_total_debt=('total_debt', 'mean'), households=('folio', 'count'))
    n13 = n12.sort_values('avg_total_debt', ascending=False)

    return n13