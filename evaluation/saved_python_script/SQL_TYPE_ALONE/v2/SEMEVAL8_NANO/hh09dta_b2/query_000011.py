def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter for adults (edad >= 18)
    adults = portad[portad["edad"] >= 18]
    
    # Merge portad with crh on 'folio'
    portad_crh = pd.merge(adults, crh, on="folio", how="inner")
    
    # Filter for households that use a plot/land for farming (su01 == 1)
    su_farming = su[su["su01"] == 1]
    
    # Merge with households that use land for farming
    merged = pd.merge(portad_crh, su_farming[["folio"]], on="folio", how="inner")
    
    # Filter for households with total debt > 0 (crh04_2 > 0) and total debt info not missing
    debt_positive = merged[(merged["crh04_2"].notna()) & (merged["crh04_2"] > 0)]
    
    # Select relevant columns: 'ent' (state), 'crh04_2' (debt), 'folio'
    debt_data = debt_positive[["ent", "crh04_2", "folio"]]
    
    # Group by 'ent' (state) and compute:
    # - mean of 'crh04_2' (average debt)
    # - count of households
    result = (
        debt_data
        .groupby("ent")
        .agg(
            average_debt=("crh04_2", "mean"),
            household_count=("folio", "count")
        )
        .reset_index()
    )
    
    # Get top 10 states with highest average debt
    top10 = result.nlargest(10, "average_debt")
    
    # Map 'ent' codes to state names for clarity
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
    top10["state"] = top10["ent"].map(state_mapping)
    
    # Select and reorder columns
    final_df = top10[["state", "average_debt", "household_count"]]
    
    return final_df