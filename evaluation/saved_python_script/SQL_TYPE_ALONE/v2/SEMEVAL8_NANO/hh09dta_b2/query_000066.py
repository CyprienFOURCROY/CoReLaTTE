def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_inr"]
    df_se = tables["ii_se"]
    df_vlh = tables["ii_vlh"]
    df_se_enriched = tables["ii_se_enriched"]
    df_vlh_enriched = tables["ii_vlh_enriched"]
    
    # Merge portad with inr on 'folio'
    merged = pd.merge(df_portad, df_in, on='folio', how='inner')
    
    # Filter households where 'edad' (age) is not null
    merged = merged[merged['edad'].notnull()]
    
    # Create a boolean column for feeling unsafe or very unsafe at home
    # 'vlh04' indicates feeling safe at home:
    # 1: Very safe, 2: Safe, 3: Unsafe, 4: Very unsafe
    unsafe_mask = merged['vlh04'].isin([3, 4])
    
    # Merge with se_enriched to get info about illness/accident/hospitalization
    merged = pd.merge(merged, df_se_enriched[['folio', 'se01b']], on='folio', how='left')
    
    # Filter households where at least one household member experienced illness/accident/hospitalization
    illness_mask = merged['se01b'] == 1
    
    # Combine both conditions: unsafe and illness
    combined_mask = unsafe_mask & illness_mask
    
    # Filter the merged DataFrame
    filtered = merged[combined_mask]
    
    # Merge with portad to get 'ent' (state)
    filtered = pd.merge(filtered, df_portad[['folio', 'ent']], on='folio', how='left')
    
    # Count households per state
    result = (
        filtered.groupby('ent')
        .size()
        .reset_index(name='household_count')
    )
    
    # Filter states with at least 50 households
    result = result[result['household_count'] >= 50]
    
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
    result = result[['state', 'household_count']]
    
    return result