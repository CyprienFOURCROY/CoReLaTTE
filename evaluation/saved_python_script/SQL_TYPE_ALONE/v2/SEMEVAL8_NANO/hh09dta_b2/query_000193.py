def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    vlh = tables["ii_vlh"]
    crh = tables["ii_crh"]
    
    # Filter households where 'vlh01c' (district persons using drugs in streets) is '3' (No) and 'vlh01d' (district prostitutes streets) is '3' (No)
    # and 'vlh01l' (people willing to help neighbors) is '3' (Disagree)
    # and 'vlh01k' (district close) is '4' (Completely disagree)
    # and 'vlh02_2' (since what year lives in house) is not '8' (DK)
    # and 'vlh04' (feel safe at home) is '3' (Unsafe) or '4' (Very unsafe)
    # and 'vlh12a' (entered force rob in HH) is '1' (Yes, into current house) or '2' (Yes, into another house)
    # and 'vlh12a_c' (no entry since 2005) is '3' (No)
    # and 'vlh13' (number of times robbed in HH) > 0
    # and 'crh04d' (total debts + interests) > 5000
    # and 'crh04d' is not '8' (DK)
    # and 'portad' (age) >= 18
    # and 'portad' (age) >= 18 and 'rel' (result interview) is not missing
    
    # Merge portad with inr to get household info
    households = portad[['folio', 'edad', 'ent', 'rel']]
    households = households[households['edad'] >= 18]
    
    # Merge with VLH data
    households_vlh = households.merge(vlh[['folio', 'vlh01c', 'vlh01d', 'vlh01l', 'vlh01k', 'vlh02_2', 'vlh04', 'vlh12a', 'vlh12a_c', 'vlh13']], on='folio', how='left')
    
    # Filter based on VLH conditions
    condition_vlh = (
        (households_vlh['vlh01c'] == 3) &  # District persons using drugs in streets? No
        & (households_vlh['vlh01d'] == 3) &  # District prostitutes streets? No
        & (households_vlh['vlh01l'] == 3) &  # People willing to help neighbors? Disagree
        & (households_vlh['vlh01k'] == 4) &  # District close? Completely disagree
        & (households_vlh['vlh02_2'] != 8) &  # Since what year lives in house? Not DK
        & (households_vlh['vlh04'].isin([3,4])) &  # Feel safe at home? Unsafe or Very unsafe
        & (households_vlh['vlh12a'].isin([1,2])) &  # Entered force rob in HH? Yes into current or other
        & (households_vlh['vlh12a_c'] == 3) &  # No entry since 2005
        & (households_vlh['vlh13'] > 0)  # Number of times robbed in HH > 0
    )
    filtered_households = households_vlh[condition_vlh]
    
    # Merge with inr to get debts info
    households_inr = filtered_households.merge(inr[['folio', 'inr04d']], on='folio', how='left')
    
    # Filter households with total debts > 5000 and not DK
    condition_inr = (
        (households_inr['inr04d'] > 5000) &
        (households_inr['inr04d'] != 8)
    )
    final_households = households_inr[condition_inr]
    
    # Count adults (edad >= 18) per state (ent)
    # Merge with portad to get age and state info
    result = final_households.merge(portad[['folio', 'edad', 'ent']], on='folio', how='left')
    adults_in_households = result[result['edad'] >= 18]
    
    # Count number of adults per state
    count_per_state = adults_in_households.groupby('ent').size().reset_index(name='adult_count')
    
    # Map 'ent' codes to state names
    state_map = {
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
    count_per_state['state'] = count_per_state['ent'].map(state_map)
    
    # Select relevant columns
    result_df = count_per_state[['state', 'adult_count']]
    
    return result_df