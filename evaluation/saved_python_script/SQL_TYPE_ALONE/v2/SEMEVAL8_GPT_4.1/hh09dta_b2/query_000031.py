def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np

    # Load tables
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Merge to get state info for each household
    df = df_vlh.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Only keep households with at least one break-in/robbery of house, business, or parcel since 2005
    # These are: vlh13a (house), vlh15a (business), vlh17a (parcel)
    # If any of these > 0, the household qualifies
    df["total_incidents"] = df[["vlh13a", "vlh15a", "vlh17a"]].fillna(0).sum(axis=1)
    df = df[df["total_incidents"] > 0]

    # Group by state, count households and sum incidents
    grouped = df.groupby("ent").agg(
        households_with_incidents=("folio", "nunique"),
        total_incidents=("total_incidents", "sum")
    ).reset_index()

    # Only keep states with at least 100 households with incidents
    grouped = grouped[grouped["households_with_incidents"] >= 100]

    # Compute average total incidents across states with any incidents (i.e., those in grouped)
    avg_total_incidents = grouped["total_incidents"].mean()

    # Only keep states whose total incidents exceeds the average
    grouped = grouped[grouped["total_incidents"] > avg_total_incidents]

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

    # Sort by total incidents descending
    grouped = grouped.sort_values("total_incidents", ascending=False)

    # Select and order columns
    result = grouped[["state", "households_with_incidents", "total_incidents"]].reset_index(drop=True)

    return result