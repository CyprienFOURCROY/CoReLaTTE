def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_inr = tables["ii_inr"]

    # Households that use a plot/land for farming (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Merge with portad to get state
    plot_with_state = su_plot.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Count households with plot per state
    plot_counts = plot_with_state.groupby("ent")["folio"].nunique().reset_index(name="households_with_plot")

    # Filter states with at least 30 households with plot
    states_30plus = plot_counts[plot_counts["households_with_plot"] >= 30]["ent"]

    # Households that produced/sold honey in last 12 months (inr02i == 1)
    honey_hh = df_inr[df_inr["inr02i"] == 1][["folio"]].drop_duplicates()

    # Households that both use plot and produced/sold honey
    plot_honey = plot_with_state.merge(honey_hh, on="folio", how="inner")

    # Count honey-producing households per state (only in states with at least 30 plot-using households)
    honey_counts = (
        plot_honey[plot_honey["ent"].isin(states_30plus)]
        .groupby("ent")["folio"]
        .nunique()
        .reset_index(name="honey_households")
    )

    # Filter states with at least 10 honey-producing households
    honey_counts = honey_counts[honey_counts["honey_households"] >= 10]

    # Sort from most to least
    honey_counts = honey_counts.sort_values("honey_households", ascending=False).reset_index(drop=True)

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
    honey_counts["state"] = honey_counts["ent"].map(state_map)
    honey_counts = honey_counts[["state", "honey_households"]]

    return honey_counts.reset_index(drop=True)