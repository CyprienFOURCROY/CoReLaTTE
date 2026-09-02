def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    vlh = tables["ii_vlh"]
    nna = tables["ii_nna"]
    
    # Filter households with at least 30 households feeling unsafe or very unsafe at home
    unsafe_mask = vlh["vlh04"].isin([3, 4])  # 3: Unsafe, 4: Very unsafe
    households_unsafe = vlh[unsafe_mask][["folio"]].drop_duplicates()

    # Filter households that do NOT own/share non-agricultural business
    nna_mask = (nna["nna01"] == 2)  # 2: No
    households_nna = nna[nna_mask][["folio"]]

    # Merge to get households satisfying both conditions
    households_filtered = pd.merge(households_unsafe, households_nna, on="folio", how="inner")

    # Count households per household ID
    household_counts = (
        households_filtered.groupby("folio")
        .size()
        .reset_index(name="count")
    )

    # Merge with portad to get 'ent' (state)
    merged = pd.merge(household_counts, portad[["folio", "ent"]], on="folio", how="left")

    # Filter for households with 'rel' indicating valid interview (assuming rel != 2 or 3 as valid)
    # Since 'rel' is not specified as missing, assume all are valid
    # Filter for households with 'ent' (state)
    # Count households per state
    state_counts = (
        merged.groupby("ent")
        .agg(total_households=("count", "sum"))
        .reset_index()
    )

    # Filter states with at least 30 households
    states_with_30 = state_counts[state_counts["total_households"] >= 30]

    # Calculate average across these states
    avg_count = states_with_30["total_households"].mean()

    # Select states with count >= average
    qualifying_states = states_with_30[states_with_30["total_households"] >= avg_count]

    # Map 'ent' codes to state names
    ent_to_state = {
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

    # Add state names
    qualifying_states["state"] = qualifying_states["ent"].map(ent_to_state)

    # Sort from highest to lowest
    result = qualifying_states[["state", "total_households"]].sort_values(by="total_households", ascending=False).reset_index(drop=True)

    return result