def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # Adults (age 18+)
    df_adults = df_portad[df_portad["edad"] >= 18].copy()

    # Merge with ah to get car ownership (ah03d1 == 1 means owns motor car)
    df_adults_ah = df_adults.merge(df_ah[["folio", "ls", "ah03d1"]], on=["folio", "ls"], how="left")

    # Keep only those where at least one HH member owns a motor car
    # For this, get all folios where any ah03d1 == 1
    folios_with_car = df_ah[df_ah["ah03d1"] == 1]["folio"].unique()
    df_adults_ah = df_adults_ah[df_adults_ah["folio"].isin(folios_with_car)]

    # Merge with vlh to get forced-entry robbery since 2005 (vlh12a_c == 3 means NO forced-entry robbery since 2005)
    df_adults_ah_vlh = df_adults_ah.merge(df_vlh[["folio", "vlh12a_c"]], on="folio", how="left")

    # Only households with vlh12a_c == 3 (No forced-entry robbery since 2005)
    df_adults_ah_vlh = df_adults_ah_vlh[df_adults_ah_vlh["vlh12a_c"] == 3]

    # Count adults per state
    adults_per_state = df_adults_ah_vlh.groupby("ent").size().reset_index(name="num_adults")

    # Calculate average number of adults per state
    avg_adults = adults_per_state["num_adults"].mean()

    # Filter states with above-average number of adults
    result = adults_per_state[adults_per_state["num_adults"] > avg_adults].copy()

    # Rank highest to lowest
    result = result.sort_values("num_adults", ascending=False).reset_index(drop=True)

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
    result["state"] = result["ent"].map(state_map)
    result = result[["state", "num_adults"]]

    return result.reset_index(drop=True)