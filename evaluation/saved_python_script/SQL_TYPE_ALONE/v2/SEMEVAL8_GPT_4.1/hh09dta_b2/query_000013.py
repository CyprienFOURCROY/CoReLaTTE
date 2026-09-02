def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_su = tables["ii_su"]

    # Adults 18+
    df_adults = df_portad[df_portad["edad"] >= 18]

    # Households with window bars facing the street (vlh07b == 1)
    df_vlh_bars = df_vlh[df_vlh["vlh07b"] == 1]

    # Households that use a plot/land for sowing/farming/vegetables (su01 == 1)
    df_su_plot = df_su[df_su["su01"] == 1]

    # Merge: adults with window bars and plot/land use
    merged = (
        df_adults
        .merge(df_vlh_bars[["folio"]], on="folio", how="inner")
        .merge(df_su_plot[["folio"]], on="folio", how="inner")
    )

    # Group by state, calculate average age and count
    result = (
        merged.groupby("ent")
        .agg(average_age=("edad", "mean"), n_adults=("edad", "size"))
        .reset_index()
    )

    # Get top 5 states by average age
    result = result.sort_values("average_age", ascending=False).head(5)

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
    result = result[["state", "average_age", "n_adults"]].reset_index(drop=True)
    return result