def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_vlh = tables["ii_vlh"]

    # Households that report using a plot/land for farming (su01==1)
    su_farming = df_su[df_su["su01"] == 1.0][["folio"]]

    # Merge with portad to get state
    merged = su_farming.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Merge with vlh to get 'feel safe at home' score
    merged = merged.merge(df_vlh[["folio", "vlh04"]], on="folio", how="left")

    # Drop rows with missing vlh04 or ent
    merged = merged.dropna(subset=["vlh04", "ent"])

    # Group by state and calculate average 'feel safe at home' score and count
    grouped = merged.groupby("ent").agg(
        avg_vlh04=("vlh04", "mean"),
        count=("folio", "count")
    ).reset_index()

    # Only keep states with at least two such households
    grouped = grouped[grouped["count"] >= 2]

    # Get five states with lowest average 'feel safe at home' score
    lowest = grouped.nsmallest(5, "avg_vlh04")

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
    lowest["state"] = lowest["ent"].map(state_map)

    # Reorder columns
    result = lowest[["ent", "state", "avg_vlh04", "count"]].reset_index(drop=True)
    return result