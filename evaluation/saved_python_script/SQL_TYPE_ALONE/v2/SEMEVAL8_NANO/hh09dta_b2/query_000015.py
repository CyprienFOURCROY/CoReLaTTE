def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    inr = tables["ii_inr"]
    
    # Filter households with dairy products sold in last 12 months (inr02a == 1)
    dairy_mask = inr["inr02a"] == 1
    households_with_dairy = inr.loc[dairy_mask, "folio"].unique()
    
    # Filter portad for these households
    portad_dairy = portad[portad["folio"].isin(households_with_dairy)]
    
    # Merge with nna to get ownership/share info
    nna_filtered = nna[nna["folio"].isin(households_with_dairy)]
    portad_nna = portad_dairy.merge(nna_filtered, on="folio", how="left")
    
    # Group by 'ent' (state)
    grouped = portad_nna.groupby("ent")
    
    # For each state, compute:
    # (a) number of households with dairy sales
    # (b) average age among these households
    # (c) number of households with at least one member owning/sharing a non-ag business (nna01 == 1)
    
    results = []
    for state_code, group in grouped:
        households = group["folio"].unique()
        count_households = len(households)
        avg_age = group["edad"].mean()
        # Check if any household in the group has nna01 == 1
        nna_state = nna[nna["folio"].isin(households)]
        households_with_non_ag = nna_state[nna_state["nna01"] == 1]["folio"].unique()
        count_non_ag = len(households_with_non_ag)
        results.append({
            "state": state_code,
            "count_households": count_households,
            "average_age": avg_age,
            "households_with_non_ag": count_non_ag
        })
    
    # Convert results to DataFrame
    df_result = pd.DataFrame(results)
    
    # Map 'ent' codes to state names for top 10 states with most households
    # Count households per state
    state_counts = df_result[["state", "count_households"]].sort_values(by="count_households", ascending=False)
    top_states = state_counts.head(10)["state"].tolist()
    
    # Filter to top 10 states
    top_df = df_result[df_result["state"].isin(top_states)]
    
    # Map state codes to names
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
    top_df["state_name"] = top_df["state"].map(state_mapping)
    
    # Select and reorder columns
    final_df = top_df[["state_name", "count_households", "average_age", "households_with_non_ag"]]
    final_df = final_df.rename(columns={
        "state_name": "State",
        "count_households": "Number of Households",
        "average_age": "Average Household Age",
        "households_with_non_ag": "Households with Non-Ag Business"
    })
    
    return final_df.reset_index(drop=True)