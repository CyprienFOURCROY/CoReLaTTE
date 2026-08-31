import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_crh'].copy()
    n2 = n1[(n1['crh02_1'] == 1)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_in'].copy()
    n5 = n4[(n4['in01a10_1'] == 3)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_ah'].copy()
    n9 = n8[(n8['ah03e'] == 1)].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(elec_owner_members=('ls', 'count'))
    n11 = n10[n10['folio'].isin(n7['folio'])].copy()
    n12 = tables['ii_portad'].copy()
    n13 = n12.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n14 = n11.merge(n13, left_on='folio', right_on='folio', how='inner')
    n15 = n14.groupby(['ent'], as_index=False).agg(avg_elec_owners_per_owner_hh=('elec_owner_members', 'mean'))
    n16 = n15.sort_values('ent', ascending=True)

    return n16