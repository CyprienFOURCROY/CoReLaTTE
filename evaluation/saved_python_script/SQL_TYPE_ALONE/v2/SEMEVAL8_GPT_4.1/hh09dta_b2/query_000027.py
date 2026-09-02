def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]

    # Only consider rows with a valid debt value (crh04_1 == 1 and crh04_2 not null)
    df_crh_debt = df_crh[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notnull())]

    # Compute the overall average of total debts + interests (crh04_2)
    avg_debt = df_crh_debt["crh04_2"].mean()

    # Get folios (households) with debt above the average
    folios_above_avg = df_crh_debt[df_crh_debt["crh04_2"] > avg_debt]["folio"].unique()

    # Adults (age >= 18) in those households
    df_adults = df_portad[(df_portad["edad"] >= 18) & (df_portad["folio"].isin(folios_above_avg))]

    # Count adults per state
    state_counts = df_adults.groupby("ent").size().reset_index(name="num_adults")

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
    state_counts["state"] = state_counts["ent"].map(state_map)

    # Sort and get top 10
    top10 = state_counts.sort_values("num_adults", ascending=False).head(10)

    # Return only state name and count
    return top10[["state", "num_adults"]].reset_index(drop=True)