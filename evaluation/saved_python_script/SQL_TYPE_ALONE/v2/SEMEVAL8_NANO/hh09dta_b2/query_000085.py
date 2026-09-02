def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    nna = tables["ii_nna"]
    
    # Filter portad for adults (age >= 18)
    adults = portad[portad["edad"] >= 18]
    
    # Merge with ah on folio and ls to get ownership info
    merged = pd.merge(adults, ah, on=["folio", "ls"], how="left")
    
    # Filter households where at least one adult owns electronic device (ah04e_1 == 1)
    owns_electronic = merged[merged["ah04e_1"] == 1]
    
    # Merge with portad to get household info
    household_info = pd.merge(owns_electronic, portad[["folio", "ent"]], on="folio", how="left")
    
    # Filter households where at least one member reports feeling very safe (vlh04 == 1) or safe (vlh04 == 2)
    # First, get households with such members
    safe_households = pd.merge(household_info, tables["ii_vlh"], on=["folio", "ls"], how="left")
    safe_households = safe_households[safe_households["vlh04"].isin([1, 2])]
    
    # Count unique households per state
    household_counts = safe_households.groupby("ent")["folio"].nunique().reset_index()
    household_counts.rename(columns={"folio": "household_count"}, inplace=True)
    
    # Calculate total households per state
    total_households = portad.groupby("ent")["folio"].nunique().reset_index()
    total_households.rename(columns={"folio": "total_households"}, inplace=True)
    
    # Merge to compute average
    merged_counts = pd.merge(household_counts, total_households, on="ent", how="left")
    merged_counts["above_average"] = merged_counts["household_count"] > (merged_counts["total_households"].mean())
    
    # Filter states with above-average households
    above_avg_states = merged_counts[merged_counts["above_average"]]
    
    # Map ent codes to state names
    ent_map = {
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
    above_avg_states["state"] = above_avg_states["ent"].map(ent_map)
    # Rank from highest to lowest
    result = above_avg_states.sort_values(by="household_count", ascending=False)[["state", "household_count"]]
    return result.reset_index(drop=True)