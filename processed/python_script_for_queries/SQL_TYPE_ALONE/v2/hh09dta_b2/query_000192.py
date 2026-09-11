import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    n1 = tables['ii_inr'].copy()
    n2 = n1[(n1['inr02d'] == 1.0)].copy()
    n3 = n2.groupby(['folio'], as_index=False).agg(eggs_last_month_total=('inr04d', 'sum'))
    n4 = tables['ii_su'].copy()
    n5 = n4[(n4['su01'] == 1.0)].copy()
    n6 = n3[n3['folio'].isin(n5['folio'])].copy()
    n7 = tables['ii_portad'].copy()
    n8 = n7.groupby(['folio'], as_index=False).agg(state_ent=('ent', 'min'))
    n9 = n6.merge(n8, left_on='folio', right_on='folio', how='inner')
    n10 = n9[(n9['state_ent'] == 20.0)].copy()
    n11 = pd.DataFrame({'national_avg_eggs_last_month_total': [n6['eggs_last_month_total'].mean()]})
    n11_national_avg_eggs_last_month_total_value = n11['national_avg_eggs_last_month_total'].iloc[0]
    n12 = n10[n10['eggs_last_month_total'] >= n11_national_avg_eggs_last_month_total_value].copy()
    n13 = n12[['folio', 'eggs_last_month_total']].copy()

    return n13