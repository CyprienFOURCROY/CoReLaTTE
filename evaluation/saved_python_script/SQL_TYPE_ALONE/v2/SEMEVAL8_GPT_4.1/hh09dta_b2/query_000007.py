def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Merge on household ID
    df = pd.merge(df_portad, df_vlh, on="folio", how="inner")

    # Filter for feeling unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_unsafe = df[df["vlh04"].isin([3.0, 4.0])]

    # Drop missing ages or states
    df_unsafe = df_unsafe.dropna(subset=["edad", "ent"])

    # Group by state, calculate average age and count
    grouped = df_unsafe.groupby("ent").agg(
        average_age=("edad", "mean"),
        n_individuals=("edad", "count")
    ).reset_index()

    # Only keep states with at least 10 such individuals
    grouped = grouped[grouped["n_individuals"] >= 10]

    # Sort by average age descending
    grouped = grouped.sort_values("average_age", ascending=False)

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
    result = grouped[["state", "average_age", "n_individuals"]].reset_index(drop=True)

    return result