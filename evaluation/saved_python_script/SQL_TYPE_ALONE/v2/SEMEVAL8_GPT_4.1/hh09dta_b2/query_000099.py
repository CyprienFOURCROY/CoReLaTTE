def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_in = tables["ii_in"]

    # Adults 18+
    df_adults = df_portad[df_portad["edad"] >= 18].copy()

    # Households that produced/sold fattening animals in last 12 months (inr02j == 1)
    df_inr_animals = df_inr[df_inr["inr02j"] == 1][["folio"]].drop_duplicates()

    # Households that received income from Other Government Program in last 12 months (in01a10_1 == 1)
    df_in_gov = df_in[df_in["in01a10_1"] == 1][["folio"]].drop_duplicates()

    # Households that satisfy both
    df_both = pd.merge(df_inr_animals, df_in_gov, on="folio", how="inner")

    # Adults living in those households
    df_adults_in_both = df_adults[df_adults["folio"].isin(df_both["folio"])]

    # Count adults per state
    adults_per_state = df_adults_in_both.groupby("ent").size().reset_index(name="num_adults")

    # Compute average across states
    avg_adults = adults_per_state["num_adults"].mean()

    # Only states with above-average number of adults
    above_avg = adults_per_state[adults_per_state["num_adults"] > avg_adults].copy()

    # Order from highest to lowest
    above_avg = above_avg.sort_values("num_adults", ascending=False).reset_index(drop=True)

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
    above_avg["state"] = above_avg["ent"].map(state_map)
    above_avg = above_avg[["state", "num_adults"]]

    return above_avg.reset_index(drop=True)