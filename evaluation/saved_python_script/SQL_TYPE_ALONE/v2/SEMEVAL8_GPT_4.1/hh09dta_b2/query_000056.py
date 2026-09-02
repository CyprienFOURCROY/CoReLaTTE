def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_in = tables["ii_in"]

    # Households that use a plot/land for farming: su01 == 1
    df_su_farm = df_su[df_su["su01"] == 1][["folio"]]

    # Households that received a positive amount directly from Other Government Program: in02a10 > 0
    df_in_gov = df_in[df_in["in02a10"].notna() & (df_in["in02a10"] > 0)][["folio"]]

    # Intersection: households that satisfy both
    df_both = pd.merge(df_su_farm, df_in_gov, on="folio", how="inner")

    # Add state info
    df_both = pd.merge(df_both, df_portad[["folio", "ent"]], on="folio", how="left")

    # Count households per state
    state_counts = df_both.groupby("ent").size().reset_index(name="num_households")

    # Compute average number of such households across all states
    avg_households = state_counts["num_households"].mean()

    # Only states with at least 50 such households and above average
    state_counts = state_counts[state_counts["num_households"] >= 50]
    state_counts = state_counts[state_counts["num_households"] > avg_households]

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

    # Sort from highest to lowest
    state_counts = state_counts.sort_values("num_households", ascending=False)

    # Select columns to return
    return state_counts[["state", "num_households"]].reset_index(drop=True)