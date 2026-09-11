def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    inr = tables["ii_inr"]
    vlh = tables["ii_vlh"]
    
    # Filter households with adult (edad >= 18)
    households_with_adult = portad[portad["edad"] >= 18]
    
    # Merge with nna to identify households with non-ag business owner/share
    households_nna = households_with_adult.merge(nna[["folio", "nna01"]], on="folio", how="inner")
    households_nna_owner = households_nna[households_nna["nna01"] == 1]
    
    # Merge with vlh to get "Feel safe at home" responses
    households_vlh = households_nna_owner.merge(vlh[["folio", "vlh04"]]], on="folio", how="inner")
    
    # Filter households that answered "Feel safe at home" (assuming non-null)
    households_vlh_answered = households_vlh[households_vlh["vlh04"].notnull()]
    
    # For each household, check if they have lived since 2005 or later
    # Merge with vlh to get "since what year lives in house" info
    households_with_year = households_vlh_answered.merge(vlh[["folio", "vlh02_2"]]], on="folio", how="inner")
    
    # Filter households that have lived since 2005 or later
    households_since_2005 = households_with_year[
        households_with_year["vlh02_2"].isin([1, 8])
    ]
    
    # Count total households per state
    households_with_state = households_since_2005.merge(portad[["folio", "ent"]]], on="folio", how="inner")
    
    # Count households per state
    state_counts = (
        households_with_state.groupby("ent")
        .agg(total_households=("folio", "nunique"))
        .reset_index()
    )
    
    # Filter states with at least 30 households
    qualifying_states = state_counts[state_counts["total_households"] >= 30]
    
    # For each qualifying state, count households with lived since 2005 or later
    count_since_2005 = (
        households_with_state.groupby("ent")
        .agg(post_2005_households=("folio", "nunique"))
        .reset_index()
    )
    
    # Merge counts
    result = qualifying_states.merge(count_since_2005, on="ent")
    
    # Calculate average of post-2005 counts
    avg_post_2005 = result["post_2005_households"].mean()
    
    # Filter states with post-2005 count >= average
    final_states = result[result["post_2005_households"] >= avg_post_2005]
    
    # Map ent to state names
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
    final_states["state_name"] = final_states["ent"].map(state_map)
    
    # Order by post-2005 count descending
    final_states_sorted = final_states.sort_values(by="post_2005_households", ascending=False)
    
    # Select relevant columns
    result_df = final_states_sorted[["state_name", "total_households", "post_2005_households"]]
    
    return result_df.reset_index(drop=True)