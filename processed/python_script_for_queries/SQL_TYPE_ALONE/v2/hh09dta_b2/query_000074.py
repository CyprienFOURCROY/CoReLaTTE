import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_inr'].copy()
    n2 = tables['ii_ah'].copy()
    n3 = n1.merge(n2, left_on='folio', right_on='folio', how='inner')
    n4 = n3[['folio', 'ls_x', 'ls_y', 'ah03d', 'inr02f']].copy()
    n5 = n4[(n4['ah03d'] == 1)].copy()
    n6 = n5.groupby(['folio'], as_index=False).agg(veh_household_rows=('folio', 'count'))
    n7 = n1[(n1['inr02f'] == 1)].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(crafts_household_rows=('folio', 'count'))
    n9 = tables['ii_portad'].copy()
    n10 = n9[(n9['ent'] == 20)].copy()
    n11 = n10.groupby(['folio'], as_index=False).agg(oax_household_rows=('folio', 'count'))
    n12 = n6[n6['folio'].isin(n11['folio'])].copy()
    n13 = n12[n12['folio'].isin(n8['folio'])].copy()
    n14 = pd.DataFrame({'household_count': [n13['folio'].count()]})

    return n14