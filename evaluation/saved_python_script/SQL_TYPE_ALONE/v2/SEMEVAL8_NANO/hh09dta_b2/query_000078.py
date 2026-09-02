def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    crh = tables["ii_crh"]
    
    # Filter households that own a motor vehicle
    ah_motor_vehicle = ah[ah["ah03d"] == 1]
    
    # Merge with crh to get debt info
    merged = pd.merge(ah_motor_vehicle, crh, on="folio", how="inner")
    
    # Filter households with total debts reported (excluding DK)
    debt_reported = merged[merged["crh04_1"].isin([1,2])]
    
    # For households with debt info, get total debts value
    debt_data = debt_reported[["folio", "ent", "edad", "ent", "crh04_2"]].dropna(subset=["crh04_2"])
    
    # Calculate overall average of total debts among these households
    overall_avg_debt = debt_data["crh04_2"].mean()
    
    # Filter households with debt above the overall average
    above_avg_debt = debt_data[debt_data["crh04_2"] > overall_avg_debt]
    
    # Merge back with portad to get state info
    result = pd.merge(above_avg_debt, portad[["folio", "ent"]], on="folio", how="left")
    
    # Count households per state
    counts = result.groupby("ent").size().reset_index(name="household_count")
    
    # Map state codes to state names
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
    counts["state"] = counts["ent"].map(state_map)
    
    # Find the maximum count
    max_count = counts["household_count"].max()
    
    # Filter states with the highest counts
    top_states = counts[counts["household_count"] == max_count][["state", "household_count"]]
    
    return top_states.reset_index(drop=True)