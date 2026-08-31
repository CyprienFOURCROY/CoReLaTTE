import pandas as pd

def run_query(tables):
    # States per household (folio)
    port = tables['ii_portad'].copy()
    port = port[['folio', 'ent']].dropna(subset=['folio'])
    port = port.groupby('folio', as_index=False).agg(ent=('ent', 'min'))

    # Households with at least one member owning a domestic appliance (ah03g == 1)
    ah = tables['ii_ah'].copy()
    if 'ah03g' in ah.columns:
        ah['ah03g_num'] = pd.to_numeric(ah['ah03g'], errors='coerce')
        ah_own = ah[ah['ah03g_num'] == 1.0][['folio']].drop_duplicates()
    else:
        ah_own = ah[[]].copy()

    # Appliance households with state
    households = ah_own.merge(port, on='folio', how='left').dropna(subset=['ent'])

    # Total such households per state (threshold base)
    totals = households.groupby('ent', as_index=False).agg(total_households=('folio', 'nunique'))

    # Forced-entry responses at household level
    vlh = tables['ii_vlh'].copy()
    vlh = vlh[['folio', 'vlh12a_a', 'vlh12a_c']].dropna(subset=['folio'])
    vlh['yes_current_flag'] = pd.to_numeric(vlh['vlh12a_a'], errors='coerce') == 1
    vlh['no_since2005_flag'] = pd.to_numeric(vlh['vlh12a_c'], errors='coerce') == 3

    by_folio = vlh.groupby('folio', as_index=False).agg(
        yes_current=('yes_current_flag', 'max'),
        no_since2005=('no_since2005_flag', 'max')
    )

    # Merge flags onto appliance households (households without a record count as False)
    flags = households[['folio', 'ent']].merge(by_folio, on='folio', how='left')
    flags['yes_current'] = flags['yes_current'].fillna(False)
    flags['no_since2005'] = flags['no_since2005'].fillna(False)

    counts = flags.groupby('ent', as_index=False).agg(
        yes_current_count=('yes_current', lambda x: int(x.sum())),
        no_since2005_count=('no_since2005', lambda x: int(x.sum()))
    )

    out = totals.merge(counts, on='ent', how='left')
    out['yes_current_count'] = out['yes_current_count'].fillna(0).astype(int)
    out['no_since2005_count'] = out['no_since2005_count'].fillna(0).astype(int)

    result = out[(out['total_households'] >= 25) & (out['no_since2005_count'] > out['yes_current_count'])].copy()
    result = result.sort_values('ent').reset_index(drop=True)

    return result
