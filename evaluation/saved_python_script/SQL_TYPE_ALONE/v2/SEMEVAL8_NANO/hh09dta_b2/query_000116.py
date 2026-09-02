def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]
    df_su_enriched = tables["ii_su_enriched"]

    # Filter households that have land for farming
    land_mask = df_su_enriched['su01'] == 1  # Yes
    df_land = df_su_enriched[land_mask][['folio']]

    # Count households with land for farming
    land_counts = df_land['folio'].value_counts()
    households_with_land = land_counts[land_counts >= 30].index

    # Filter households with land for farming and at least 30 households
    df_farming = df_su_enriched[df_su_enriched['folio'].isin(households_with_land)]

    # Merge with portad to get state info
    df_merged = df_farming.merge(df_portad[['folio', 'ent']], on='folio', how='left')

    # Filter households that produce or sell honey in last 12 months
    honey_mask = df_inr['inr02i'] == 1  # Yes
    df_honey = df_inr[honey_mask][['folio']]

    # Count honey-producing households per household
    honey_counts = df_honey['folio'].value_counts()

    # Filter households that produce/sell honey
    households_with_honey = honey_counts.index

    # Filter the main dataframe to include only households with honey
    df_final = df_merged[df_merged['folio'].isin(households_with_honey)]

    # Count honey households per state
    result = (
        df_final.groupby('ent')
        .size()
        .reset_index(name='honey_households')
    )

    # Filter states with at least 10 honey-producing households
    result_filtered = result[result['honey_households'] >= 10]

    # Map state codes to state names
    state_mapping = {
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

    # Add state names
    result_filtered['state'] = result_filtered['ent'].map(state_mapping)

    # Sort from most to least honey-producing households
    result_sorted = result_filtered.sort_values(by='honey_households', ascending=False)

    # Select only state name and count
    final_result = result_sorted[['state', 'honey_households']].reset_index(drop=True)

    return final_result