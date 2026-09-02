def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    in_df = tables["ii_in"]
    se_df = tables["ii_se"]
    
    # Filter households that received the "Other Government Program" with positive amount
    in_df_filtered = in_df[
        (in_df["in02a10"] > 0) &  # Amount received directly from Other Government Program > 0
    ]
    
    # Filter households that experienced household illness/accident/hospitalization in last five years
    se_filtered = se_df[
        (se_df["se01b"] == 1)  # HH: disease/accident/hospital HHM? = Yes
    ]
    
    # Merge in_df_filtered with se_filtered on 'folio'
    merged_in_se = pd.merge(in_df_filtered, se_filtered[["folio"]], on="folio", how="inner")
    
    # Filter households that have more adults (age >= 18) than the average number of adults among households that received Liconsa milk
    # First, find households that received Liconsa milk
    in_liconsa = in_df[in_df["in03a"] == 1]
    # Merge with portad to get ages
    portad_in_liconsa = pd.merge(in_liconsa, portad[["folio", "edad"]], on="folio", how="inner")
    # Calculate number of adults per household
    portad['adult'] = portad['edad'] >= 18
    adults_count = portad.groupby('folio')['adult'].sum().reset_index()
    # Calculate average number of adults among households that received Liconsa
    avg_adults_liconsa = adults_count['adult'].mean()
    
    # Merge merged_in_se with portad to get ages
    merged_full = pd.merge(merged_in_se, portad[['folio', 'edad']], on='folio', how='left')
    # Count adults per household
    adults_per_household = merged_full.groupby('folio')['edad'].apply(lambda x: (x >= 18).sum()).reset_index(name='adults_count')
    # Filter households with more adults than the average
    households_more_adults = adults_per_household[adults_per_household['adults_count'] > avg_adults_liconsa]
    # Get list of folios satisfying this
    folios_more_adults = households_more_adults['folio']
    
    # Filter the merged_in_se for these households
    final_households = merged_full[merged_full['folio'].isin(folios_more_adults)]
    
    # For each state, compute the average amount received directly from the "Other Government Program" among households that meet all criteria
    result = (
        final_households
        .groupby("ent")
        .agg(avg_amount=("in02a10", "mean"))
        .reset_index()
    )
    
    # Map 'ent' codes to state names for clarity
    state_map = {
        2: "Baja California",
        3: "Baja California Sur",
        4: "Campeche",
        5: "Coahuila",
        6: "Colima",
        7: "Chiapas",
        9: "Distrito Federal",
        10: "Durango",
        11: "Guanajuato",
        12: "Guerrero",
        13: "Hidalgo",
        14: "Jalisco",
        15: "Estado de México",
        16: "Michoacán",
        17: "Morelos",
        18: "Nayarit",
        19: "Nuevo León",
        20: "Oaxaca",
        21: "Puebla",
        22: "Querétaro",
        25: "Sinaloa",
        26: "Sonora",
        28: "Tamaulipas",
        29: "Tlaxcala",
        30: "Veracruz",
        31: "Yucatán",
        32: "Zacatecas"
    }
    result['state'] = result['ent'].map(state_map)
    
    # Rank from highest to lowest average amount
    result_sorted = result.sort_values(by='avg_amount', ascending=False).reset_index(drop=True)
    
    # Select only 'state' and 'avg_amount' columns for output
    output = result_sorted[['state', 'avg_amount']]
    
    return output