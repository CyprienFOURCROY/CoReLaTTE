def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_in = tables["ii_in"]

    # Adults only
    df_adults = df_portad[df_portad["edad"] >= 18]

    # Households that reported producing/selling dairy products in last 12 months (inr02a == 1)
    # Only keep households that answered yes or no to receiving Liconsa milk (in03a == 1 or 3)
    df_in_liconsa = df_in[ df_in["in03a"].isin([1.0, 3.0]) ][["folio"]].drop_duplicates()
    df_inr_dairy = df_inr[df_inr["inr02a"] == 1.0][["folio"]].drop_duplicates()

    # Households that meet both criteria
    eligible_folios = pd.merge(df_in_liconsa, df_inr_dairy, on="folio", how="inner")["folio"].unique()

    # Adults in those households
    df_adults_eligible = df_adults[df_adults["folio"].isin(eligible_folios)]

    # Group by state and count adults
    adults_by_state = df_adults_eligible.groupby("ent").size().reset_index(name="num_adults")

    # Compute average number of adults across all states
    avg_adults = adults_by_state["num_adults"].mean()

    # Only states with above-average number of adults
    above_avg_states = adults_by_state[adults_by_state["num_adults"] > avg_adults].copy()

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
    above_avg_states["state"] = above_avg_states["ent"].map(state_map)
    above_avg_states = above_avg_states[["state", "num_adults"]].sort_values("num_adults", ascending=False).reset_index(drop=True)
    return above_avg_states