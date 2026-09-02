def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter households with no savings
    # crh01_1a == 1 indicates "Do not have savings"
    no_savings = crh[crh["crh01_1a"] == 1][["folio"]]
    
    # Filter households that do not use a plot/land for farming
    # su su01 == 3 indicates "No"
    su_no_plot = su[su["su01"] == 3][["folio"]]
    
    # Merge to find households that satisfy both conditions
    merged = pd.merge(no_savings, su_no_plot, on="folio", how="inner", suffixes=('_crh', '_su'))
    
    # Count households per household ID (folio)
    counts = merged.groupby("folio").size().reset_index(name="count")
    
    # Filter households with at least 50 such households
    households_with_50_or_more = counts[counts["count"] >= 50]
    
    # Merge with portad to get state info
    result = pd.merge(households_with_50_or_more, portad[["folio", "ent"]], on="folio", how="left")
    
    # Count number of households per state (ent)
    state_counts = result.groupby("ent").size().reset_index(name="household_count")
    
    # Map state codes to state names (optional, not required, but for clarity)
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
    state_counts["state"] = state_counts["ent"].map(state_mapping)
    
    # Order from highest to lowest
    state_counts = state_counts.sort_values(by="household_count", ascending=False).reset_index(drop=True)
    
    # Select only state name and count for output
    output = state_counts[["state", "household_count"]]
    
    return output