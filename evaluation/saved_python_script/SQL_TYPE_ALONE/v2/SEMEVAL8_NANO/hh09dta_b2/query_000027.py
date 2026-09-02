def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    
    # Filter households with reported debt (crh04_1 != 8 which indicates DK)
    crh_debt = crh[crh["crh04_1"] != 8].copy()
    # Calculate total debts including interests
    crh_debt["total_debt"] = crh_debt["crh04_2"]
    
    # Compute overall average of total debts
    overall_avg_debt = crh_debt["total_debt"].mean()
    
    # Filter households with total debt above the overall average
    high_debt_households = crh_debt[crh_debt["total_debt"] > overall_avg_debt]
    
    # Get household IDs with high debt
    high_debt_folios = high_debt_households["folio"]
    
    # Merge with portad to get age and ent
    merged = pd.merge(portad, high_debt_folios.to_frame(), on="folio", how="inner")
    
    # Filter adults (age >= 18)
    adults = merged[merged["edad"] >= 18]
    
    # Count number of adults per state (ent)
    counts = adults.groupby("ent").size().reset_index(name="adult_count")
    
    # Get top 10 states with highest number of adults
    top10 = counts.nlargest(10, "adult_count")
    
    # Map state codes to state names (using provided info)
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
    top10["state_name"] = top10["ent"].map(state_map)
    return top10[["state_name", "adult_count"]]