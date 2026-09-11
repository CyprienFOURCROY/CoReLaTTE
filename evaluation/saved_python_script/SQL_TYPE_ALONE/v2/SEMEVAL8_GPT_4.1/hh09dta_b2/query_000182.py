def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Get relevant columns
    df_vlh_sub = df_vlh[["folio", "vlh18a"]].copy()
    # Only households with at least one incident since 2005
    df_vlh_sub = df_vlh_sub[df_vlh_sub["vlh18a"].notna() & (df_vlh_sub["vlh18a"] > 0)]
    # Compute overall average among these households
    overall_avg = df_vlh_sub["vlh18a"].mean()
    # Households above the average
    df_above_avg = df_vlh_sub[df_vlh_sub["vlh18a"] > overall_avg]

    # Merge with state info
    df_portad_sub = df_portad[["folio", "ent"]].drop_duplicates("folio")
    df_merged = pd.merge(df_above_avg, df_portad_sub, on="folio", how="left")

    # Count households per state
    state_counts = df_merged.groupby("ent")["folio"].nunique().reset_index(name="num_households")
    # Get top 5 states
    top5 = state_counts.sort_values("num_households", ascending=False).head(5)

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
    top5["state"] = top5["ent"].map(state_map)
    # Reorder columns
    result = top5[["ent", "state", "num_households"]].reset_index(drop=True)
    return result