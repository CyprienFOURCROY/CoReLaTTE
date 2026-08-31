import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_ah'].copy()
    n2 = n1[['folio', 'ah04e_2']].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(asset_electronics_value=('ah04e_2', 'max'))
    n4 = tables['ii_vlh'].copy()
    n5 = n4[(n4['vlh18a'] > 0)].copy()
    n6 = tables['ii_su'].copy()
    n7 = n6[(n6['su01'] == 1)].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = tables['ii_portad'].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n11 = n8.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11.merge(n3, left_on='folio', right_on='folio', how='inner')
    n13 = pd.DataFrame({'mean_asset_electronics_value': [n12['asset_electronics_value'].mean()]})
    n13_mean_asset_electronics_value_value = n13['mean_asset_electronics_value'].iloc[0]
    n14 = n12[n12['asset_electronics_value'] > n13_mean_asset_electronics_value_value].copy()
    n15 = n14.groupby(['ent'], as_index=False).agg(avg_asset_electronics_value=('asset_electronics_value', 'mean'), n_households=('folio', 'count'))
    n16 = n15.sort_values('avg_asset_electronics_value', ascending=False)

    return n16