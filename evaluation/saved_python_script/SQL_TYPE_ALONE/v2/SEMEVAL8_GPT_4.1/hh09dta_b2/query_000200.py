def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Households with at least one resident aged 70 or older
    df_aged_70 = df_portad[df_portad["edad"] >= 70]
    hh_with_70plus = set(df_aged_70["folio"].unique())

    # Households that reported receiving income from '70 y más' program in last 12 months
    # in01a11_1: 1 = Participates in the program and have received income
    df_70ymas = df_in[df_in["in01a11_1"] == 1]
    hh_with_70ymas_income = set(df_70ymas["folio"].unique())

    # Intersection: households that satisfy both conditions
    hh_both = hh_with_70plus & hh_with_70ymas_income

    # For each household, get its state (ent)
    df_hh_state = df_portad[["folio", "ent"]].drop_duplicates()
    df_hh_state = df_hh_state[df_hh_state["folio"].isin(hh_both)]

    # Count number of such households per state
    state_counts = df_hh_state.groupby("ent")["folio"].nunique().reset_index()
    state_counts = state_counts.rename(columns={"folio": "num_households"})

    # Compute average across states
    avg = state_counts["num_households"].mean()

    # Filter states with at least the average number of such households
    result = state_counts[state_counts["num_households"] >= avg].copy()

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
    result = result[["state", "num_households"]].sort_values("num_households", ascending=False).reset_index(drop=True)
    return result