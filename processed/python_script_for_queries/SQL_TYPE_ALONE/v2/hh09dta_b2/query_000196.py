import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_su'].copy()
    n2 = n1[(n1['su01'] == 1.0)].copy()
    n3 = tables['ii_se'].copy()
    n4 = n3[(n3['se01d'] == 1.0)].copy()
    n5 = n2[n2['folio'].isin(n4['folio'])].copy()
    n6 = n5[['folio', 'su234']].copy()
    n7 = n6.groupby(['folio'], as_index=False).agg(seeds_expense=('su234', 'mean'))
    n8 = tables['ii_portad'].copy()
    n9 = n8[['folio', 'ent']].copy()
    n10 = n9.groupby(['folio'], as_index=False).agg(ent=('ent', 'max'))
    n11 = n7.merge(n10, left_on='folio', right_on='folio', how='inner')
    n12 = n11.groupby(['ent'], as_index=False).agg(n_households=('folio', 'count'), avg_seeds_expense=('seeds_expense', 'mean'))
    n13 = pd.DataFrame({'overall_avg_seeds': [n11['seeds_expense'].mean()]})
    n14 = n12[(n12['n_households'] >= 10)].copy()
    n13_overall_avg_seeds_value = n13['overall_avg_seeds'].iloc[0]
    n15 = n14[n14['avg_seeds_expense'] > n13_overall_avg_seeds_value].copy()
    n16 = n15.sort_values('avg_seeds_expense', ascending=False)
    n17 = n16[['ent', 'n_households', 'avg_seeds_expense']].copy()

    return n17