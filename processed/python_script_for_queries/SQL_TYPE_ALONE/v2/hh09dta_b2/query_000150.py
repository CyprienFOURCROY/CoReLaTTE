import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_portad'].copy()
    n2 = n1.groupby(['folio'], as_index=False).agg(ent=('ent', 'min'), resp_age=('edad', 'mean'))
    n3 = n2[['folio', 'ent', 'resp_age']].copy()
    n4 = tables['ii_vlh'].copy()
    n5 = n4[(n4['vlh04'].isin([3.0, 4.0]))].copy()
    n6 = tables['ii_crh'].copy()
    n7 = n6[(n6['crh04_1'] == 1.0)].copy()
    n8 = n5.merge(n7, left_on='folio', right_on='folio', how='inner')
    n9 = n8.merge(n3, left_on='folio', right_on='folio', how='inner')
    n10 = n9.groupby(['ent'], as_index=False).agg(mean_total_debt_unsafe=('crh04_2', 'mean'), mean_age_unsafe=('resp_age', 'mean'), n_unsafe_with_value=('folio', 'count'))
    n11 = pd.DataFrame({'national_mean_total_debt': [n7['crh04_2'].mean()]})
    n11_national_mean_total_debt_value = n11['national_mean_total_debt'].iloc[0]
    n12 = n10[n10['mean_total_debt_unsafe'] > n11_national_mean_total_debt_value].copy()
    n13 = n12.sort_values('mean_total_debt_unsafe', ascending=False)

    return n13