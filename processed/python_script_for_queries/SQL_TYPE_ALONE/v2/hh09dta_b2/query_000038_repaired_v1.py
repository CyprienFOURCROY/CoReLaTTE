import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # Load tables
    df_portad = tables.get('ii_portad', pd.DataFrame()).copy()
    df_ah = tables.get('ii_ah', pd.DataFrame()).copy()
    df_vlh = tables.get('ii_vlh', pd.DataFrame()).copy()

    # Guard clauses for required columns
    required_cols_portad = {'folio', 'edad'}
    required_cols_ah = {'folio', 'ah03d'}
    required_cols_vlh = {'folio', 'vlh04'}

    if not required_cols_portad.issubset(df_portad.columns):
        return pd.DataFrame({
            'total_unsafe_households': [0],
            'unsafe_with_adult_vehicle_owner': [0]
        })
    if not required_cols_ah.issubset(df_ah.columns):
        return pd.DataFrame({
            'total_unsafe_households': [0],
            'unsafe_with_adult_vehicle_owner': [0]
        })
    if not required_cols_vlh.issubset(df_vlh.columns):
        return pd.DataFrame({
            'total_unsafe_households': [0],
            'unsafe_with_adult_vehicle_owner': [0]
        })

    # Determine Oaxaca households (ent == 20). Prefer ent from ii_portad; fallback to ii_vlh if needed.
    if 'ent' in df_portad.columns:
        ent_series = pd.to_numeric(df_portad['ent'], errors='coerce')
        hh_oax = (
            df_portad.loc[ent_series == 20, ['folio']]
            .drop_duplicates()
        )
    elif 'ent' in df_vlh.columns:
        ent_series_v = pd.to_numeric(df_vlh['ent'], errors='coerce')
        hh_oax = (
            df_vlh.loc[ent_series_v == 20, ['folio']]
            .drop_duplicates()
        )
    else:
        # If we cannot determine state, return zeros to avoid misleading counts
        return pd.DataFrame({
            'total_unsafe_households': [0],
            'unsafe_with_adult_vehicle_owner': [0]
        })

    # Unsafe households that answered the safety question (vlh04 in [3,4])
    vlh04_num = pd.to_numeric(df_vlh['vlh04'], errors='coerce')
    df_unsafe = df_vlh.loc[vlh04_num.isin([3, 4]), ['folio']].drop_duplicates()
    df_unsafe_oax = df_unsafe.merge(hh_oax, on='folio', how='inner')

    # Adults (edad >= 18) in Oaxaca
    edad_num = pd.to_numeric(df_portad['edad'], errors='coerce')
    adults_oax = (
        df_portad.loc[edad_num >= 18, ['folio']]
        .merge(hh_oax, on='folio', how='inner')
    )

    # Vehicle owners (ah03d == 1) in Oaxaca
    ah03d_num = pd.to_numeric(df_ah['ah03d'], errors='coerce')
    owners_oax = (
        df_ah.loc[ah03d_num == 1, ['folio']]
        .merge(hh_oax, on='folio', how='inner')
    )

    # Try to ensure adult and owner refer to the same person by detecting a common person identifier
    possible_person_cols = [
        'n_ren', 'num_ren', 'renglon', 'id_persona', 'id_per', 'id', 'ren', 'linea', 'rph', 'ren_ind', 'consec', 'con', 'reng'
    ]
    person_key = None
    for col in possible_person_cols:
        if col in df_portad.columns and col in df_ah.columns:
            person_key = col
            break

    if person_key is not None:
        adults_oax_pid = (
            df_portad.loc[edad_num >= 18, ['folio', person_key]]
            .merge(hh_oax, on='folio', how='inner')
            .dropna(subset=[person_key])
            .drop_duplicates()
        )
        owners_oax_pid = (
            df_ah.loc[ah03d_num == 1, ['folio', person_key]]
            .merge(hh_oax, on='folio', how='inner')
            .dropna(subset=[person_key])
            .drop_duplicates()
        )
        adult_owner_hh = (
            adults_oax_pid.merge(owners_oax_pid, on=['folio', person_key], how='inner')[['folio']]
            .drop_duplicates()
        )
    else:
        # Fallback: require household to have at least one adult and at least one owner (may be different persons)
        adult_owner_hh = (
            adults_oax.drop_duplicates().merge(owners_oax.drop_duplicates(), on='folio', how='inner')
        )

    # Intersect with unsafe Oaxaca households
    unsafe_oax_unique = df_unsafe_oax.drop_duplicates()
    unsafe_with_adult_owner = unsafe_oax_unique.merge(adult_owner_hh.drop_duplicates(), on='folio', how='inner')

    total_unsafe_households = int(unsafe_oax_unique['folio'].nunique())
    unsafe_with_adult_vehicle_owner = int(unsafe_with_adult_owner['folio'].nunique())

    result = pd.DataFrame({
        'total_unsafe_households': [total_unsafe_households],
        'unsafe_with_adult_vehicle_owner': [unsafe_with_adult_vehicle_owner]
    })

    return result
