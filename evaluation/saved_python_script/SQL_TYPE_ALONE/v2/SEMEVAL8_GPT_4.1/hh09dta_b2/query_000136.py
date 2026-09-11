def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_inr = tables["ii_inr"]

    # Households with positive amount received directly from Other Government Program
    # in02a10: Amount received directly Other Government Program
    df_in_pos = df_in[df_in["in02a10"].notna() & (df_in["in02a10"] > 0)]

    # Merge with state info
    df_merged = df_in_pos.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Count households per state
    state_counts = df_merged.groupby("ent")["folio"].nunique().reset_index()
    state_counts = state_counts.rename(columns={"folio": "num_households"})

    # Filter states with at least 30 such households
    states_30plus = state_counts[state_counts["num_households"] >= 30]["ent"]

    # Keep only those states in the merged df
    df_merged_30plus = df_merged[df_merged["ent"].isin(states_30plus)]

    # For each such state, count number of unique households
    result = df_merged_30plus.groupby("ent")["folio"].nunique().reset_index()
    result = result.rename(columns={"folio": "num_households"})

    # Now, for each such state, count how many of these households reported producing/selling dairy products in last 12 months
    # inr02a: 1 = Yes, 3 = No
    df_inr_dairy = df_inr[df_inr["inr02a"] == 1][["folio"]].drop_duplicates()

    # Merge to see which of the selected households produced/sold dairy
    df_merged_30plus_dairy = df_merged_30plus.merge(df_inr_dairy, on="folio", how="inner")

    dairy_counts = df_merged_30plus_dairy.groupby("ent")["folio"].nunique().reset_index()
    dairy_counts = dairy_counts.rename(columns={"folio": "num_households_dairy"})

    # Merge both counts
    final = result.merge(dairy_counts, on="ent", how="left")
    final["num_households_dairy"] = final["num_households_dairy"].fillna(0).astype(int)

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
    final["state"] = final["ent"].map(state_map)
    final = final[["state", "num_households", "num_households_dairy"]].sort_values("state").reset_index(drop=True)
    return final