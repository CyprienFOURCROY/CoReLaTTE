def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    
    # Filter households that use land for farming
    land_use_mask = df_inr["inr02a"] == 1
    df_inr_land = df_inr[land_use_mask]
    
    # Filter households that produced/sold honey in the last 12 months
    honey_mask = df_inr_land["inr02i"] == 1
    df_inr_honey = df_inr_land[honey_mask]
    
    # Get list of relevant household IDs
    household_ids = df_inr_honey["folio"].unique()
    
    # Filter portad for these households
    df_portad_filtered = df_portad[df_portad["folio"].isin(household_ids)]
    
    # Merge to get individual ages for these households
    df_merged = pd.merge(df_portad_filtered, df_inr_honey[["folio"]], on="folio", how="inner")
    
    # For each household, get the minimum age of interviewed individual
    household_age = (
        df_portad[df_portad["folio"].isin(household_ids)]
        .groupby("folio")["edad"]
        .min()
        .reset_index()
    )
    
    # Calculate overall average age for these households
    overall_avg_age = household_age["edad"].mean()
    
    # Merge to get state info
    df_households = pd.merge(household_age, df_portad[["folio", "ent"]], on="folio", how="left")
    
    # Calculate average age per state
    state_avg = (
        df_households
        .groupby("ent")["edad"]
        .mean()
        .reset_index()
    )
    
    # Filter states with average age higher than overall average
    result = state_avg[state_avg["edad"] > overall_avg_age]
    
    # Map state codes to state names
    state_mapping = {
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
    result["state"] = result["ent"].map(state_mapping)
    result = result[["state", "edad"]].sort_values(by="edad", ascending=False).reset_index(drop=True)
    result.columns = ["State", "Average Age"]
    return result