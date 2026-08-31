import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # Tables
    portad = tables.get('ii_portad', pd.DataFrame()).copy()
    vlh = tables.get('ii_vlh', pd.DataFrame()).copy()
    nna = tables.get('ii_nna', pd.DataFrame()).copy()

    if portad.empty:
        return pd.DataFrame(columns=['ent', 'n_households'])

    # Ensure necessary columns exist
    for col in ['folio', 'ent', 'edad']:
        if col not in portad.columns:
            return pd.DataFrame(columns=['ent', 'n_households'])

    # Coerce edad to numeric
    portad['edad_num'] = pd.to_numeric(portad['edad'], errors='coerce')

    # States that have at least one interviewed person aged >= 50
    states_with_50 = (
        portad.loc[portad['edad_num'] >= 50, 'ent']
        .dropna()
        .drop_duplicates()
    )

    # Households that have at least one member younger than 30
    young_households = (
        portad.loc[portad['edad_num'] < 30, ['folio', 'ent']]
        .dropna(subset=['folio', 'ent'])
        .drop_duplicates()
    )

    # Keep only households in states that have someone aged >= 50
    young_households = young_households[young_households['ent'].isin(states_with_50)]

    if young_households.empty:
        return pd.DataFrame(columns=['ent', 'n_households'])

    # Condition (b): vlh18a == 0 (explicit zero, not missing)
    if 'vlh18a' not in vlh.columns or 'folio' not in vlh.columns:
        return pd.DataFrame(columns=['ent', 'n_households'])
    vlh['_vlh18a_num'] = pd.to_numeric(vlh['vlh18a'], errors='coerce')
    vlh_zero = vlh.loc[vlh['_vlh18a_num'] == 0, ['folio']].dropna().drop_duplicates()

    # Condition (c): nna01 == 1
    if 'nna01' not in nna.columns or 'folio' not in nna.columns:
        return pd.DataFrame(columns=['ent', 'n_households'])
    nna['_nna01_num'] = pd.to_numeric(nna['nna01'], errors='coerce')
    nna_yes = nna.loc[nna['_nna01_num'] == 1, ['folio']].dropna().drop_duplicates()

    # Merge conditions
    eligible = (
        young_households
        .merge(vlh_zero, on='folio', how='inner')
        .merge(nna_yes, on='folio', how='inner')
        .drop_duplicates(subset=['folio'])
    )

    if eligible.empty:
        return pd.DataFrame(columns=['ent', 'n_households'])

    # Count households by state and sort descending
    result = (
        eligible.groupby('ent', as_index=False)
        .agg(n_households=('folio', 'nunique'))
        .sort_values('n_households', ascending=False)
    )

    return result
