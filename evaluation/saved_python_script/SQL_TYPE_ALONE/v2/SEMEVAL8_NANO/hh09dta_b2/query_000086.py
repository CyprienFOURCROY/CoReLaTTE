def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_se = tables["ii_se"]
    df_vlh = tables["ii_vlh"]

    # Merge portad with in, se, vlh on 'folio'
    df = df_portad.merge(df_in, on='folio', how='inner') \
                  .merge(df_se, on='folio', how='inner') \
                  .merge(df_vlh, on='folio', how='inner')

    # Filter households that report feeling unsafe or very unsafe at home
    # 'vlh04' codes:
    # 1: Very safe, 2: Safe, 3: Unsafe, 4: Very unsafe
    unsafe_mask = df['vlh04'].isin([3, 4])

    # Filter households that have not experienced forced home entry since 2005
    # 'vlh12a' codes:
    # 1: Yes, into current house
    # 2: Yes, into another house
    # 3: No
    no_forced_entry_mask = df['vlh12a'] == 3

    # Filter households with at least 30 such households
    filtered_df = df[unsafe_mask & no_forced_entry_mask]
    household_counts = filtered_df.groupby('ent').size()
    sufficient_counts = household_counts[household_counts >= 30].index
    filtered_df = filtered_df[filtered_df['ent'].isin(sufficient_counts)]

    # Among these, select households that report feeling unsafe or very unsafe
    # Already filtered by 'vlh04' in [3,4]
    # Compute mean of 'vlh01x' (home safety scale)
    # 'vlh01x' codes:
    # 1: Never, 2: Rarely, 3: Frequently, 4: Always, 8: DK
    # Higher = more unsafe, so include only valid scores (excluding 8)
    valid_safety_mask = filtered_df['vlh01x'] != 8
    df_valid = filtered_df[valid_safety_mask]

    # Group by 'ent' (state), compute mean and count
    result = df_valid.groupby('ent').agg(
        mean_safety=('vlh01x', 'mean'),
        household_count=('folio', 'count')
    ).reset_index()

    # Filter states with at least 30 households
    result = result[result['household_count'] >= 30]

    # Order by highest mean safety (more unsafe)
    result = result.sort_values(by='mean_safety', ascending=False)

    # Map 'ent' codes to state names
    ent_map = {
        2: 'Baja California',
        3: 'Baja California Sur',
        4: 'Campeche',
        5: 'Coahuila',
        6: 'Colima',
        7: 'Chiapas',
        9: 'Distrito Federal',
        10: 'Durango',
        11: 'Guanajuato',
        12: 'Guerrero',
        13: 'Hidalgo',
        14: 'Jalisco',
        15: 'Estado de México',
        16: 'Michoacán',
        17: 'Morelos',
        18: 'Nayarit',
        19: 'Nuevo León',
        20: 'Oaxaca',
        21: 'Puebla',
        22: 'Querétaro',
        25: 'Sinaloa',
        26: 'Sonora',
        28: 'Tamaulipas',
        29: 'Tlaxcala',
        30: 'Veracruz',
        31: 'Yucatán',
        32: 'Zacatecas'
    }
    result['state'] = result['ent'].map(ent_map)

    # Select relevant columns
    final_result = result[['state', 'mean_safety', 'household_count']]

    return final_result