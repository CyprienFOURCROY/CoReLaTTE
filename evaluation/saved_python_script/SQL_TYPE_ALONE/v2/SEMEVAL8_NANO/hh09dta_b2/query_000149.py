def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]
    
    # Filter households in Oaxaca (ent == 15) with at least one adult (edad >= 18)
    # First, get households with at least one adult
    adults = df_portad[df_portad['edad'] >= 18]
    households_with_adults = adults['folio'].unique()
    
    # Filter households in Oaxaca
    oaxaca_households = df_portad[df_portad['ent'] == 15]['folio'].unique()
    
    # Households in Oaxaca with at least one adult
    oaxaca_adult_households = set(households_with_adults).intersection(set(oaxaca_households))
    
    # Filter households that received Liconsa milk in last 12 months
    # in ii_in: 'in03a' == 1 means received Liconsa Milk
    households_liconsa = df_in[
        (df_in['folio'].isin(oaxaca_adult_households)) & 
        (df_in['in03a'] == 1)
    ]['folio'].unique()
    
    # Filter households in the above set
    households_final = set(households_liconsa)
    
    # For these households, check ownership of motor vehicle in ii_ah
    df_ah_filtered = df_ah[
        (df_ah['folio'].isin(households_final))
    ][['folio', 'ah03d']]
    
    # Determine households with at least one member owning a motor vehicle
    # Group by household and check if any member owns a vehicle
    ownership = df_ah_filtered.groupby('folio')['ah03d'].apply(lambda x: (x == 1).any())
    
    # Count households with at least one member owning a motor vehicle
    count_with_vehicle = ownership.sum()
    count_without_vehicle = len(ownership) - count_with_vehicle
    
    result_df = pd.DataFrame({
        'households_with_motor_vehicle': [count_with_vehicle],
        'households_without_motor_vehicle': [count_without_vehicle]
    })
    
    return result_df