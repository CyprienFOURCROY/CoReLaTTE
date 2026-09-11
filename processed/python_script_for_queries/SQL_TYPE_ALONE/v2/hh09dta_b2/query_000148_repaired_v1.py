import pandas as pd


def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # Copy tables
    portad = tables['ii_portad'].copy()
    crh = tables['ii_crh'].copy()
    vlh = tables['ii_vlh'].copy()
    indiv = tables['ii_in'].copy()

    # Ensure necessary columns are numeric where applicable
    for df, cols in [
        (indiv, ['edad']),
        (crh, ['crh04_1', 'crh04_2']),
        (vlh, ['vlh04'])
    ]:
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')

    # Map household to a single state from ii_portad (one state per folio)
    if 'folio' not in portad.columns or 'ent' not in portad.columns:
        return pd.DataFrame(columns=['state', 'avg_debt'])
    state_by_folio = (
        portad[['folio', 'ent']]
        .dropna(subset=['folio'])
        .drop_duplicates(subset=['folio'])
    )

    # Households with at least one interviewed individual aged 60+
    if 'folio' not in indiv.columns or 'edad' not in indiv.columns:
        return pd.DataFrame(columns=['state', 'avg_debt'])
    seniors = (
        indiv.loc[indiv['edad'] >= 60, ['folio']]
        .dropna(subset=['folio'])
        .groupby('folio', as_index=False)
        .size()
        .rename(columns={'size': 'senior_count'})
    )
    seniors = seniors[seniors['senior_count'] >= 1]

    # Households with reported value for total debts + interests
    if 'folio' not in crh.columns or 'crh04_1' not in crh.columns or 'crh04_2' not in crh.columns:
        return pd.DataFrame(columns=['state', 'avg_debt'])
    crh_filtered = crh.loc[crh['crh04_1'] == 1, ['folio', 'crh04_2']].copy()
    crh_filtered = crh_filtered.dropna(subset=['folio', 'crh04_2'])
    # Ensure one row per household (if multiple, take the mean to avoid duplication bias)
    crh_by_folio = crh_filtered.groupby('folio', as_index=False).agg(crh04_2=('crh04_2', 'mean'))

    # Households that feel unsafe or very unsafe at home (vlh04 in {3,4})
    if 'folio' not in vlh.columns or 'vlh04' not in vlh.columns:
        return pd.DataFrame(columns=['state', 'avg_debt'])
    vlh_unsafe = vlh.loc[vlh['vlh04'].isin([3, 4]), ['folio']].dropna(subset=['folio']).drop_duplicates('folio')

    # Merge all criteria ensuring one row per household
    hh = (
        state_by_folio
        .merge(seniors[['folio', 'senior_count']], on='folio', how='inner')
        .merge(crh_by_folio, on='folio', how='inner')
        .merge(vlh_unsafe, on='folio', how='inner')
    )

    if hh.empty:
        return pd.DataFrame(columns=['state', 'avg_debt'])

    # Compute average debt by state
    by_state = hh.groupby('ent', as_index=False).agg(avg_debt=('crh04_2', 'mean'))
    by_state = by_state.rename(columns={'ent': 'state'})

    # Overall average debt for eligible households
    overall_avg = hh['crh04_2'].mean()

    # Filter states with avg at or above overall average, then get top 1
    result = by_state[by_state['avg_debt'] >= overall_avg].sort_values('avg_debt', ascending=False).head(1)

    # Ensure final columns
    return result[['state', 'avg_debt']].reset_index(drop=True)
