def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Merge to get state info
    df = df_vlh.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Compute total break-ins/robberies since 2005
    # vlh13a: Number of times robbed in HH since 2005.
    # vlh15a: Number times rob/force business since 2005.
    # vlh17a: Number of times entered/rob parcel since 2005.
    # Only consider households with at least one such incident
    df["total_incidents"] = df[["vlh13a", "vlh15a", "vlh17a"]].fillna(0).sum(axis=1)
    qualifying = df[df["total_incidents"] > 0].copy()

    # Compute national average
    national_avg = qualifying["total_incidents"].mean()

    # Group by state, compute average and count
    state_stats = (
        qualifying.groupby("ent")
        .agg(avg_incidents=("total_incidents", "mean"), n_households=("folio", "count"))
        .reset_index()
    )

    # Only states with at least 30 qualifying households and avg > national avg
    result = state_stats[
        (state_stats["n_households"] >= 30) & (state_stats["avg_incidents"] > national_avg)
    ].sort_values("avg_incidents", ascending=False)

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
    result = result[["state", "avg_incidents", "n_households"]].reset_index(drop=True)
    return result