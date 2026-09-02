def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_in = tables["ii_in"]
    df_nna = tables["ii_nna"]

    # Merge portad with su and in on 'folio'
    df_merged = df_portad.merge(df_su, on='folio', how='inner').merge(df_in, on='folio', how='inner')

    # Filter households that use land for farming (su01 == 1)
    df_farming = df_merged[df_merged['su01'] == 1]

    # Filter households with positive amount directly from 'in02a13' (Opciones Productivas)
    df_positive_opciones = df_farming[df_farming['in02a13'] > 0]

    # Group by 'ent' (state) and count households
    group_counts = df_positive_opciones.groupby('ent').size().reset_index(name='household_count')

    # Filter states with at least 50 such households
    states_with_min = group_counts[group_counts['household_count'] >= 50]

    # For each state, compute total households that both use land and received positive amount from 'in02a13'
    # Already filtered households in df_positive_opciones
    # Count households per state
    state_households = df_positive_opciones.groupby('ent').size().reset_index(name='count')

    # Merge with states_with_min to keep only states with >=50 households
    result_df = states_with_min.merge(state_households, on='ent')

    # Map 'ent' codes to state names
    ent_to_state = {
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
    result_df['state_name'] = result_df['ent'].map(ent_to_state)

    # Select relevant columns and sort by household count descending
    final_df = result_df[['state_name', 'count']].sort_values(by='count', ascending=False).reset_index(drop=True)

    return final_df