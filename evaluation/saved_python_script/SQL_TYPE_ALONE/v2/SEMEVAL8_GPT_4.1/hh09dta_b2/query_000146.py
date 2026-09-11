def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_ah = tables["ii_ah"]
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Households where at least one member owns a motor vehicle (ah03d == 1)
    hh_with_vehicle = df_ah[df_ah["ah03d"] == 1]["folio"].unique()

    # Filter to these households in ii_portad to get state info
    df_portad_vehicle = df_portad[df_portad["folio"].isin(hh_with_vehicle)][["folio", "ent"]].drop_duplicates()

    # Filter to these households in ii_vlh to get 'Feel safe at home?' (vlh04)
    df_vlh_vehicle = df_vlh[df_vlh["folio"].isin(hh_with_vehicle)][["folio", "vlh04"]]

    # Merge to get state and safety score per household
    df_vehicle = df_portad_vehicle.merge(df_vlh_vehicle, on="folio", how="inner")

    # Remove missing vlh04
    df_vehicle = df_vehicle[~df_vehicle["vlh04"].isna()]

    # Compute overall average 'Feel safe at home?' for these households
    overall_avg = df_vehicle["vlh04"].mean()

    # Group by state, compute count and average
    grouped = df_vehicle.groupby("ent").agg(
        household_count=("folio", "nunique"),
        avg_vlh04=("vlh04", "mean")
    ).reset_index()

    # Filter: at least 30 households and avg > overall_avg
    filtered = grouped[(grouped["household_count"] >= 30) & (grouped["avg_vlh04"] > overall_avg)]

    # Rank from highest (least safe) to lowest average
    filtered = filtered.sort_values("avg_vlh04", ascending=False)

    # Map state codes to names
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
    filtered["state"] = filtered["ent"].map(state_map)

    # Reorder columns
    result = filtered[["state", "avg_vlh04", "household_count"]].reset_index(drop=True)
    return result