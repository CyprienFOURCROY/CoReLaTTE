import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'))
    n3 = n2[['folio', 'ent']].copy()
    n4 = tables['ii_vlh'].copy()
    n5 = n4[(n4['vlh18a'] != None) & (n4['vlh18a'] > 0)].copy()
    n6 = n5.merge(n3, left_on='folio', right_on='folio', how='inner')
    n7 = n6.groupby(['ent'], as_index=False).agg(avg_vlh18a=('vlh18a', 'mean'), n_households=('folio', 'count'))
    n8 = n7[(n7['n_households'] >= 30)].copy()
    n9 = pd.DataFrame({'national_avg_vlh18a': [n6['vlh18a'].mean()]})
    n9_national_avg_vlh18a_value = n9['national_avg_vlh18a'].iloc[0]
    n10 = n8[n8['avg_vlh18a'] > n9_national_avg_vlh18a_value].copy()
    n11 = n10.sort_values('avg_vlh18a', ascending=False)
    n12 = n11[['ent', 'avg_vlh18a', 'n_households']].copy()

    return n12