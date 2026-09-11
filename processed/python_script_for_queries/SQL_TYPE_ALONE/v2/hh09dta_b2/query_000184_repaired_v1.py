import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # Copy and normalize key columns
    crh = tables['ii_crh'].copy()
    nna = tables['ii_nna'].copy()
    portad = tables['ii_portad'].copy()

    # Ensure folio is a consistent key type for merging
    for df in (crh, nna, portad):
        if 'folio' in df.columns:
            df['folio'] = df['folio'].astype(str)

    # Coerce numeric fields to numeric where relevant
    for col in ['crh02_1', 'crh03_1', 'crh02_2', 'crh03_2']:
        if col in crh.columns:
            crh[col] = pd.to_numeric(crh[col], errors='coerce')

    # Overall average owed among value-reporting households (crh02_1 == 1)
    crh_owed_any = crh[crh['crh02_1'] == 1]
    avg_owed = crh_owed_any['crh02_2'].mean(skipna=True)

    # Households with reported exact owed values (crh02_1 == 1), aggregated by folio
    owed_per_folio = (
        crh_owed_any[['folio', 'crh02_2']]
        .groupby('folio', as_index=False)
        .agg(crh02_2=('crh02_2', 'max'))
    )

    # Households with reported exact paid values (crh03_1 == 1), aggregated by folio
    crh_paid_any = crh[crh['crh03_1'] == 1]
    paid_per_folio = (
        crh_paid_any[['folio', 'crh03_2']]
        .groupby('folio', as_index=False)
        .agg(crh03_2=('crh03_2', 'max'))
    )

    # Households that reported both owed and paid exact values
    both = owed_per_folio.merge(paid_per_folio, on='folio', how='inner')

    # Filter: paid exceeds owed
    both = both[(both['crh03_2'] > both['crh02_2'])]

    # Filter: paid exceeds overall average owed among value-reporting households
    if pd.notna(avg_owed):
        both = both[both['crh03_2'] > avg_owed]
    else:
        # If average is NaN (no value-reporting households), then none can satisfy the condition
        both = both.iloc[0:0]

    # Households where any member owns/shares a non-ag business (nna01 == 1)
    if 'nna01' in nna.columns:
        nna['nna01'] = pd.to_numeric(nna['nna01'], errors='coerce')
        nna_hh = nna[nna['nna01'] == 1][['folio']].drop_duplicates()
    else:
        nna_hh = nna[['folio']].iloc[0:0]

    eligible_hh = both.merge(nna_hh, on='folio', how='inner')[['folio']].drop_duplicates()

    # Map households to state (ent) via person roster; ensure one ent per household
    ent_map = portad[['folio', 'ent']].dropna(subset=['folio'])
    ent_map = ent_map.groupby('folio', as_index=False).agg(ent=('ent', 'first'))

    hh_with_ent = eligible_hh.merge(ent_map, on='folio', how='inner')

    # Count distinct households per state
    result = (
        hh_with_ent.groupby('ent', as_index=False)
        .agg(n_households=('folio', 'nunique'))
        .sort_values('n_households', ascending=False)
    )

    return result
