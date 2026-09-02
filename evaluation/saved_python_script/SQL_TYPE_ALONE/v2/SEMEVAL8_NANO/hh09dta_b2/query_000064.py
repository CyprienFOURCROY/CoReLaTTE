def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    
    # Filter households that answered 'yes' or 'no' to receiving Liconsa milk
    # inr02a: 1=Yes, 3=No
    inr_liconsa = inr[inr["inr02a"].isin([1, 3])]
    
    # Merge portad with inr on 'folio'
    merged = pd.merge(portad, inr_liconsa[["folio", "ls"]], on="folio", how="inner")
    
    # Filter for individuals aged 18+ (edad >= 18)
    adults = merged[merged["edad"] >= 18]
    
    # Filter for production/selling dairy products: inr02a == 1 (Yes)
    dairy_production = adults[adults["inr02a"] == 1]
    
    # Count number of such adults per household
    household_counts = dairy_production.groupby("folio").size().reset_index(name="adult_count")
    
    # Merge back with portad to get 'ent' (state)
    household_info = pd.merge(household_counts, portad[["folio", "ent"]], on="folio", how="left")
    
    # Calculate average number of adults per state
    state_avg = household_info.groupby("ent")["adult_count"].mean().reset_index()
    
    # Compute overall average
    overall_avg = household_info["adult_count"].mean()
    
    # Select states with above-average number of adults
    above_avg_states = state_avg[state_avg["adult_count"] > overall_avg]
    
    # Map 'ent' codes to state names (from metadata)
    ent_mapping = {
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
    above_avg_states["state"] = above_avg_states["ent"].map(ent_mapping)
    
    # Prepare final output
    result = above_avg_states[["state", "adult_count"]].rename(columns={"adult_count": "average_adults"})
    
    return result