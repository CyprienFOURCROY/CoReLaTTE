def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]

    # Merge to get state and household info
    df = df_in.merge(df_portad[["folio", "ent"]], on="folio", how="left")
    df = df.merge(df_vlh[["folio", "vlh18a"]], on="folio", how="left")

    # Filter: households that received a positive amount directly from Other Government Program
    df = df[df["in02a10"].notna() & (df["in02a10"] > 0)]

    # Only keep rows with non-null vlh18a (total times robbed since 2005)
    df = df[df["vlh18a"].notna()]

    # Compute overall average
    overall_avg = df["vlh18a"].mean()

    # Group by state, compute count and average
    grouped = df.groupby("ent").agg(
        household_count=("folio", "count"),
        avg_robberies_since_2005=("vlh18a", "mean")
    ).reset_index()

    # Only states with at least 30 such households
    grouped = grouped[grouped["household_count"] >= 30]

    # Only states with average above overall average
    result = grouped[grouped["avg_robberies_since_2005"] > overall_avg]

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
    result = result[["state", "household_count", "avg_robberies_since_2005"]].sort_values("avg_robberies_since_2005", ascending=False).reset_index(drop=True)
    return result