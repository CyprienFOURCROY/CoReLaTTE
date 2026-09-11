import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[(n1['edad'] >= 18)].copy()
    n3 = n2.groupby(['ent', 'folio'], as_index=False).agg(n_adults_in_household=('ls', 'count'))
    n4 = n3[['ent', 'folio']].copy()
    n5 = n4.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'))
    n6 = n5[(n5['n_households'] >= 50)].copy()
    n7 = tables['ii_ah'].copy()
    n8 = n7[(n7['ah03e'] == 1)].copy()
    n9 = n8[['folio']].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(n_rows=('folio', 'count'))
    n11 = n10[['folio']].copy()
    n12 = n4[n4['folio'].isin(n11['folio'])].copy()
    n13 = n12.groupby(['ent'], as_index=False).agg(n_households_with_electronic=('folio', 'count'))
    n14 = n13[n13['ent'].isin(n6['ent'])].copy()
    n15 = n14.sort_values('n_households_with_electronic', ascending=False)

    return n15