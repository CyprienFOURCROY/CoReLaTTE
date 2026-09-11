def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_ah = tables["ii_ah"]
    df_portad = tables["ii_portad"]

    # Filter: owns electronic device (ah03e == 1) AND reported value (ah04e_2 not null)
    mask = (df_ah["ah03e"] == 1.0) & (~df_ah["ah04e_2"].isna())
    df_own = df_ah.loc[mask, ["folio", "ah04e_2"]]

    # Only one record per household (folio)
    df_own = df_own.drop_duplicates(subset=["folio"])

    # Merge with state info
    df_state = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])
    df_merged = df_own.merge(df_state, on="folio", how="inner")

    # Compute overall average
    overall_avg = df_merged["ah04e_2"].mean()

    # Group by state, count households, compute average
    grouped = df_merged.groupby("ent").agg(
        num_households=("folio", "count"),
        avg_value=("ah04e_2", "mean")
    ).reset_index()

    # Only states with at least 30 households and avg > overall_avg
    result = grouped[(grouped["num_households"] >= 30) & (grouped["avg_value"] > overall_avg)]

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

    # Reorder and select columns
    result = result[["state", "num_households", "avg_value"]].sort_values("avg_value", ascending=False).reset_index(drop=True)
    return result