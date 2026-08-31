import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # Base tables
    portad = tables['ii_portad'].copy()
    vlh = tables['ii_vlh'].copy()
    nna = tables['ii_nna'].copy()
    su = tables['ii_su'].copy()

    # Keep only needed columns and deduplicate
    p = portad[['folio', 'ent']].drop_duplicates()

    vlh_unsafe = vlh[vlh['vlh04'].isin([3, 4])][['folio']].drop_duplicates()

    su_no_farming = su[su['su01'] == 3][['folio']].drop_duplicates()

    nna_valid = nna[nna['nna01'].isin([1, 2])][['folio', 'nna01']].copy()
    # Aggregate to household level: if any member/record says yes (1), mark household as 1
    nna_hh = nna_valid.groupby('folio', as_index=False)['nna01'].max().rename(columns={'nna01': 'nna01_hh'})

    # Combine criteria at household level
    df = (
        p.merge(vlh_unsafe, on='folio', how='inner')
         .merge(su_no_farming, on='folio', how='inner')
         .merge(nna_hh, on='folio', how='inner')
    )

    # Count households with nna01_hh == 1 per state
    df_yes = df[df['nna01_hh'] == 1]
    counts = df_yes.groupby('ent', as_index=False).agg(yes_households=('folio', 'nunique'))

    # Nationwide average per-state count
    avg_yes = counts['yes_households'].mean()

    # Filter for Oaxaca (20) and Puebla (21) below the national average
    result = counts[counts['ent'].isin([20, 21])]
    result = result[result['yes_households'] < avg_yes]
    result = result.sort_values('yes_households', ascending=True)[['ent', 'yes_households']]

    return result
