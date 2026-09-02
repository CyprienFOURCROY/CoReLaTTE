def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_vlh = tables["ii_vlh"]

    # Households that feel unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]]

    # Households that do NOT report owning or sharing a non-ag business (nna01 == 2)
    df_nna_no_biz = df_nna[df_nna["nna01"] == 2.0][["folio"]]

    # Merge to get folios that satisfy both conditions
    unsafe_no_biz = pd.merge(df_vlh_unsafe, df_nna_no_biz, on="folio", how="inner")

    # Get state for each folio (one row per household)
    df_portad_hh = df_portad.drop_duplicates(subset=["folio"])[["folio", "ent"]]

    merged = pd.merge(unsafe_no_biz, df_portad_hh, on="folio", how="inner")

    # Count households per state
    state_counts = merged.groupby("ent")["folio"].nunique().reset_index(name="household_count")

    # Only states with at least 30 households
    state_counts_30 = state_counts[state_counts["household_count"] >= 30].copy()

    # Compute average across qualifying states
    avg_count = state_counts_30["household_count"].mean()

    # States with counts at or above the average
    state_counts_final = state_counts_30[state_counts_30["household_count"] >= avg_count].copy()

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
    state_counts_final["state"] = state_counts_final["ent"].map(state_map)

    # Sort from highest to lowest
    result = state_counts_final.sort_values("household_count", ascending=False)[["state", "household_count"]].reset_index(drop=True)

    return result