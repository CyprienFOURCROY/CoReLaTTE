def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter for adults (edad >= 18)
    adults = portad[portad["edad"] >= 18]
    
    # Merge portad with crh on 'folio'
    merged_crh = pd.merge(adults, crh, on="folio", how="inner")
    
    # Filter for households that use a plot/land for farming (su01 == 1)
    su_farming = su[su["su01"] == 1]
    
    # Merge with households that farm
    merged = pd.merge(merged_crh, su_farming[["folio"]], on="folio", how="inner")
    
    # Filter for households with positive total debt including interest (crh04_1 == 1)
    debt_positive = merged[merged["crh04_1"] == 1]
    
    # Remove households with missing 'crh04_2' (total debt in pesos)
    debt_positive = debt_positive[debt_positive["crh04_2"].notna()]
    
    # Group by 'ent' (state)
    grouped = debt_positive.groupby("ent")
    
    # Calculate mean total debt in pesos and count households per state
    result = grouped.agg(
        average_debt_in_pesos=pd.NamedAgg(column="crh04_2", aggfunc="mean"),
        household_count=pd.NamedAgg(column="folio", aggfunc="count")
    ).reset_index()
    
    # Select top 10 states with highest average debt
    top10 = result.sort_values(by="average_debt_in_pesos", ascending=False).head(10)
    
    # Map 'ent' codes to state names (optional, not required, but for clarity)
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
    top10["state_name"] = top10["ent"].map(state_mapping)
    
    # Return the final DataFrame with state name, average debt, and household count
    return top10[["state_name", "average_debt_in_pesos", "household_count"]]