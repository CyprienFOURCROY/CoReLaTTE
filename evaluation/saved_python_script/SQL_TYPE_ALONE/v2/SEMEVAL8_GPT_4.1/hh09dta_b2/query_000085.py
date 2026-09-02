def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]

    # 1. Households with at least one adult (18+)
    df_adults = df_portad[df_portad["edad"] >= 18]
    hh_with_adult = set(df_adults["folio"].unique())

    # 2. Households with at least one member who owns an electronic device (ah03e == 1)
    df_electronic = df_ah[df_ah["ah03e"] == 1]
    hh_with_electronic = set(df_electronic["folio"].unique())

    # 3. Households that report feeling very safe or safe at home (vlh04 == 1 or 2)
    df_safe = df_vlh[df_vlh["vlh04"].isin([1.0, 2.0])]
    hh_feel_safe = set(df_safe["folio"].unique())

    # 4. Intersection: households that meet all three criteria
    hh_selected = hh_with_adult & hh_with_electronic & hh_feel_safe

    # 5. Get state for each household
    df_hh_state = df_portad[["folio", "ent"]].drop_duplicates()
    df_hh_state = df_hh_state[df_hh_state["folio"].isin(hh_selected)]

    # 6. Count households per state
    state_counts = df_hh_state.groupby("ent")["folio"].nunique().reset_index(name="num_households")

    # 7. Compute average number of such households across all states
    avg_households = state_counts["num_households"].mean()

    # 8. Filter states with above-average number of such households
    state_counts_above_avg = state_counts[state_counts["num_households"] > avg_households]

    # 9. Map state codes to names
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
    state_counts_above_avg["state"] = state_counts_above_avg["ent"].map(state_map)

    # 10. Sort by number of households descending
    result = state_counts_above_avg.sort_values("num_households", ascending=False)[["state", "num_households"]].reset_index(drop=True)

    return result