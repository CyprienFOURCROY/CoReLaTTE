import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_se'].copy()
    n2 = n1[(n1['se01b'] == 1)].copy()
    n3 = n2[['folio']].copy()
    n4 = tables['ii_in'].copy()
    n5 = n4[(n4['in01a10_1'] == 1)].copy()
    n6 = n5[['folio']].copy()
    n7 = n3[n3['folio'].isin(n6['folio'])].copy()
    n8 = tables['ii_portad'].copy()
    n9 = n8[n8['folio'].isin(n7['folio'])].copy()
    n10 = n9[(n9['ent'] == 20)].copy()
    n13 = n10[['folio', 'ls', 'ent', 'edad']].copy()

    return n13