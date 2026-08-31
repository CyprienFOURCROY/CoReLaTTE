import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1[['folio', 'ent']].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(ent_max=('ent', 'max'))
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1.0)].copy()
    n6 = n5[['folio', 'su234']].copy()
    n7 = n6.merge(n3, left_on='folio', right_on='folio', how='inner')
    n8 = n7.groupby(['ent_max'], as_index=False).agg(avg_seeds=('su234', 'mean'))
    n9 = n8[(n8['avg_seeds'] > 1000.0)].copy()
    n10 = pd.DataFrame({'overall_avg_seeds': [n7['su234'].mean()]})
    n10_overall_avg_seeds_value = n10['overall_avg_seeds'].iloc[0]
    n11 = n9[n9['avg_seeds'] >= n10_overall_avg_seeds_value].copy()
    n12 = n11.sort_values('avg_seeds', ascending=False)

    return n12