def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    su = tables["ii_su"]
    
    # Filter portad for adults (age >= 18)
    adults = portad[portad["edad"] >= 18]
    
    # Filter for households with window bars street ("vlh07b" == 1)
    vlh_bars = vlh[vlh["vlh07b"] == 1]
    
    # Filter for households that use a plot/land for sowing/farming/vegetables ("su01" == 1)
    households_with_plot = su[su["su01"] == 1]
    
    # Merge adults with households with plot on "folio"
    adults_with_household = pd.merge(adults, households_with_plot[["folio"]], on="folio", how="inner")
    
    # Merge the above with vlh on "folio" to get households with window bars
    adults_with_bars = pd.merge(adults_with_household, vlh_bars[["folio"]], on="folio", how="inner")
    
    # Now, for each adult, get their "ent" (state)
    adults_with_bars = pd.merge(adults_with_bars, portad[["folio", "ent"]], on="folio", how="left")
    
    # Group by "ent" (state) and compute mean age and count
    result = (
        adults_with_bars
        .groupby("ent")
        .agg(average_age=("edad", "mean"), count_adults=("folio", "count"))
        .reset_index()
    )
    
    # Map "ent" codes to state names for clarity (optional, but not required)
    # Create a dictionary for state code to name
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
    result["state"] = result["ent"].map(state_map)
    
    # Select top 5 states with highest average age
    top5 = (
        result
        .sort_values(by="average_age", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )
    
    # Keep only state name, average age, and number of adults
    final_df = top5[["state", "average_age", "count_adults"]]
    
    return final_df