def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    se = tables["ii_se"]
    
    # Merge ah and se on folio and ls
    merged = pd.merge(ah, se, on=["folio", "ls"], how="inner")
    
    # Filter households that experienced a disease, accident, or hospitalization in last 5 years
    # Columns: se01b (disease/accident/hospital)
    # Value: 1 indicates yes
    disease_mask = merged["se01b"] == 1
    filtered = merged[disease_mask]
    
    # For each household, check if they have at least 2 such households
    household_counts = filtered.groupby("folio").size()
    households_with_min2 = household_counts[household_counts >= 2].index
    
    # Filter to only households with at least 2 such households
    filtered = filtered[filtered["folio"].isin(households_with_min2)]
    
    # For these households, compute average number of electronic devices (ah03e)
    # First, group by folio and compute mean of ah03e
    household_avg = filtered.groupby("folio")["ah03e"].mean()
    
    # Merge with portad to get state info
    household_info = pd.DataFrame({"folio": household_avg.index, "avg_ah03e": household_avg.values})
    household_info = pd.merge(household_info, portad[["folio", "ent"]], on="folio", how="left")
    
    # For each state, compute number of households and average electronic devices
    state_stats = household_info.groupby("ent").agg(
        household_count=pd.NamedAgg(column="folio", aggfunc="count"),
        average_devices=pd.NamedAgg(column="avg_ah03e", aggfunc="mean")
    ).reset_index()
    
    # Filter states with at least 2 households
    state_stats = state_stats[state_stats["household_count"] >= 2]
    
    # Select top 10 states by average_devices
    top_states = state_stats.nlargest(10, "average_devices")
    
    # Map state codes to state names (from metadata)
    state_code_map = {
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
    top_states["state_name"] = top_states["ent"].map(state_code_map)
    
    # Prepare final output DataFrame
    result = top_states[["state_name", "household_count", "average_devices"]]
    result.columns = ["State", "Households", "Avg Electronic Devices"]
    
    return result