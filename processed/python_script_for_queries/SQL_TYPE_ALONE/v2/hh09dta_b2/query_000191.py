import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent_state=('ent', 'min'))
    n3 = tables['ii_vlh'].copy()
    n4 = tables['ii_nna'].copy()
    n5 = n3[(n3['vlh04'].isin([1.0, 2.0]))].copy()
    n6 = n4[(n4['nna01'] == 1.0)].copy()
    n7 = n5.merge(n6, left_on='folio', right_on='folio', how='inner')
    n8 = n7.merge(n2, left_on='folio', right_on='folio', how='inner')
    n9 = n8[['folio', 'ent_state', 'vlh18a']].copy()
    n10 = n9.groupby(['ent_state'], as_index=False).agg(avg_vlh18a=('vlh18a', 'mean'), n_households=('folio', 'count'))
    n11 = n10[(n10['n_households'] >= 50)].copy()
    n12 = pd.DataFrame({'nat_avg_vlh18a': [n9['vlh18a'].mean()]})
    n12_nat_avg_vlh18a_value = n12['nat_avg_vlh18a'].iloc[0]
    n13 = n11[n11['avg_vlh18a'] > n12_nat_avg_vlh18a_value].copy()
    n14 = n13[['ent_state', 'avg_vlh18a', 'n_households']].copy()
    n15 = n14.sort_values('avg_vlh18a', ascending=False)

    return n15