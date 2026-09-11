def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]

    # Households that use a plot/land for farming (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Households that produced/sold BOTH meat (inr02c == 1) AND eggs (inr02d == 1) in last 12 months
    inr_meat_eggs = df_inr[(df_inr["inr02c"] == 1) & (df_inr["inr02d"] == 1)][["folio"]].drop_duplicates()

    # Intersection: folios that satisfy both conditions
    folios = pd.Series(np.intersect1d(su_plot["folio"].values, inr_meat_eggs["folio"].values))

    # Filter individuals in those households
    df_filtered = df_portad[df_portad["folio"].isin(folios)]

    # Only keep rows with non-null age and state
    df_filtered = df_filtered[df_filtered["edad"].notnull() & df_filtered["ent"].notnull()]

    # Compute overall average age
    overall_avg_age = df_filtered["edad"].mean()

    # Group by state, compute average age and count
    state_stats = (
        df_filtered.groupby("ent")
        .agg(avg_age=("edad", "mean"), n_individuals=("edad", "count"))
        .reset_index()
    )

    # Only states with at least 30 individuals and avg_age > overall_avg_age
    state_stats = state_stats[state_stats["n_individuals"] >= 30]
    state_stats = state_stats[state_stats["avg_age"] > overall_avg_age]

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
    state_stats["state"] = state_stats["ent"].map(state_map)

    # Sort from highest to lowest average age
    state_stats = state_stats.sort_values("avg_age", ascending=False)

    # Select and reorder columns
    result = state_stats[["state", "avg_age", "n_individuals"]].reset_index(drop=True)

    return result