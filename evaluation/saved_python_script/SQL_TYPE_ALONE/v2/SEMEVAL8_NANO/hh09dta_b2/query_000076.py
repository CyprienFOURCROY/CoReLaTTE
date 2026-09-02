def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    # Filter households that report using a plot/land for sowing, farming, or vegetables
    land_use_mask = df_vlh["su01"] == 1  # Yes
    df_land_use = df_vlh[land_use_mask][["folio"]]

    # Merge with portad to get 'ent' (state) info
    df_merged = pd.merge(df_land_use, df_portad[["folio", "ent"]], on="folio", how="left")

    # Count total households per state with land use
    land_use_counts = df_merged.groupby("ent").size()

    # Filter states with at least 30 such households
    states_with_min_households = land_use_counts[land_use_counts >= 30].index

    # Filter merged data to only include these states
    df_filtered = df_merged[df_merged["ent"].isin(states_with_min_households)]

    # Merge with portad again to get 'edad' if needed, but not necessary here
    # We only need 'ent' and 'vlh01h' (Feel safe at home?)
    df_vlh_filtered = pd.merge(df_filtered, df_vlh[["folio", "vlh04"]], on="folio", how="left")

    # Calculate average 'vlh04' (Feel safe at home?) per state
    avg_safety = (
        df_vlh_filtered.groupby("ent")["vlh04"]
        .mean()
        .reset_index()
        .rename(columns={"ent": "state", "vlh04": "avg_feel_safe"})
    )

    # Rank states from safest (lowest avg) to least safe
    avg_safety_sorted = avg_safety.sort_values("avg_feel_safe", ascending=True).reset_index(drop=True)

    # Map 'ent' codes to state names for clarity (optional, but not required)
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
    avg_safety_sorted["state_name"] = avg_safety_sorted["state"].map(state_mapping)

    # Return the sorted DataFrame with state name and average safety rating
    return avg_safety_sorted[["state_name", "avg_feel_safe"]]