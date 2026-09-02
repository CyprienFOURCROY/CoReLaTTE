def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]

    # Only keep households with a recorded value for total debts + interests (crh04_1 == 1) and a non-null value in crh04_2
    df_crh_valid = df_crh[(df_crh["crh04_1"] == 1) & (df_crh["crh04_2"].notnull())]

    # Merge with state info
    df_merged = pd.merge(df_crh_valid[["folio", "crh04_2"]], df_portad[["folio", "ent"]], on="folio", how="left")

    # Compute overall average
    overall_avg = df_merged["crh04_2"].mean()

    # Group by state, compute average and count
    state_stats = df_merged.groupby("ent").agg(
        avg_total_debt_plus_interest=("crh04_2", "mean"),
        num_households=("crh04_2", "count")
    ).reset_index()

    # Filter states with average above overall average
    state_stats = state_stats[state_stats["avg_total_debt_plus_interest"] > overall_avg]

    # Sort from highest to lowest average
    state_stats = state_stats.sort_values("avg_total_debt_plus_interest", ascending=False)

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
    state_stats = state_stats[["state", "avg_total_debt_plus_interest", "num_households"]]

    return state_stats.reset_index(drop=True)