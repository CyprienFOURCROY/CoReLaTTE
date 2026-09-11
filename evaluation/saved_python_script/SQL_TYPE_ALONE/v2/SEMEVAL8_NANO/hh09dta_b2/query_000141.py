def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_ah = tables["ii_ah"]
    df_en = tables["ii_ah"]
    
    # Filter households that own electronic devices and reported their value
    df_elec = df_ah[(df_ah["ah03e"] == 1) & (df_ah["ah04e_2"].notna())]
    
    # Calculate overall average value of electronic devices
    overall_avg = df_elec["ah04e_2"].mean()
    
    # Count households per state with at least 30 households
    # First, merge with portad to get 'ent' (state)
    df_merged = df_elec.merge(tables["ii_portad"][["folio", "ent"]], on="folio", how="left")
    
    # Group by state and compute count and mean
    state_stats = (
        df_merged.groupby("ent")
        .agg(
            household_count=("folio", "nunique"),
            avg_value=("ah04e_2", "mean")
        )
        .reset_index()
    )
    
    # Filter states with at least 30 households
    states_with_enough_households = state_stats[state_stats["household_count"] >= 30]
    
    # Filter states where average device value > overall average
    qualifying_states = states_with_enough_households[
        states_with_enough_households["avg_value"] > overall_avg
    ]
    
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
    
    # Add state names
    qualifying_states["state"] = qualifying_states["ent"].map(ent_mapping)
    
    # Select and rename columns for output
    result = qualifying_states[["state", "household_count", "avg_value"]]
    result.columns = ["state", "number_of_households", "average_value"]
    
    return result