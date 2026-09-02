def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_su = tables["ii_su"]

    # Only households that report using a plot/land for sowing/farming/vegetable (su01 == 1)
    df_su_plot = df_su[df_su["su01"] == 1.0][["folio"]]

    # Merge with vlh to get 'vlh04' (Feel safe at home?)
    df_vlh_plot = pd.merge(df_su_plot, df_vlh[["folio", "vlh04"]], on="folio", how="inner")

    # Merge with portad to get 'ent' (state)
    df_plot = pd.merge(df_vlh_plot, df_portad[["folio", "ent"]], on="folio", how="inner")

    # Only consider valid 'vlh04' values (1-4)
    df_plot = df_plot[df_plot["vlh04"].isin([1.0, 2.0, 3.0, 4.0])]

    # Group by state, compute count and mean
    grouped = df_plot.groupby("ent").agg(
        n_households=("folio", "count"),
        avg_feel_safe=("vlh04", "mean")
    ).reset_index()

    # Only states with at least 30 such households
    grouped = grouped[grouped["n_households"] >= 30]

    # Rank from safest (lowest avg) to least safe
    grouped = grouped.sort_values("avg_feel_safe", ascending=True).reset_index(drop=True)

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
    grouped["state"] = grouped["ent"].map(state_map)

    # Reorder columns
    result = grouped[["state", "ent", "n_households", "avg_feel_safe"]]

    return result.reset_index(drop=True)