def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    ah = tables["ii_ah"]

    # Filter households with no forced-entry robbery since 2005
    # Conditions:
    # - vlh12a_c == 3 (No forced rob since 2005)
    # - ah03d1 == 1 (Household owns motor car)
    # - vlh12a == 1 (Entered force rob in HH into current house)
    # - vlh12b == 2 or 1 (rob in HH or other house, but we focus on current house)
    # Actually, to be precise, we want households with no forced rob since 2005:
    #   vlh12a_c == 3
    #   and at least one household member owns a motor car (ah03d1 == 1)
    #   and household has entered force rob in current house (vlh12a == 1)
    #   and the household is in the dataset (so we join on folio)
    # Note: The 'vlh' table has household-level info, 'ah' has household info, 'portad' has individual info.

    # Filter households with no forced rob since 2005
    households_no_rob_2005 = vlh[vlh["vlh12a_c"] == 3]["folio"].unique()

    # Filter households where at least one member owns a motor car
    households_with_car = ah[(ah["ah03d1"] == 1)]["folio"].unique()

    # Filter households that satisfy both conditions
    target_households = set(households_no_rob_2005).intersection(set(households_with_car))

    # Filter portad for these households
    portad_filtered = portad[portad["folio"].isin(target_households)]

    # Filter for adults (age >= 18)
    adults = portad_filtered[portad_filtered["edad"] >= 18]

    # Group by 'ent' (state) and count number of adults
    adults_count = adults.groupby("ent").size().reset_index(name="adults_count")

    # Calculate average number of adults across all states in this subset
    avg_adults = adults_count["adults_count"].mean()

    # Select states with above-average number of adults
    above_avg_states = adults_count[adults_count["adults_count"] > avg_adults]

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
    above_avg_states["state"] = above_avg_states["ent"].map(ent_mapping)

    # Rank states by number of adults (descending)
    result = above_avg_states.sort_values(by="adults_count", ascending=False)[["state", "adults_count"]]

    return result.reset_index(drop=True)