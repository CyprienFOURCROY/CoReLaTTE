def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    nna = tables["ii_nna"]
    su = tables["ii_su"]
    
    # Filter households with 'edad' (age) indicating very safe or safe at home
    # According to the description, 'vlh04' indicates feeling safe at home:
    # 1: Very safe, 2: Safe, 3: Unsafe, 4: Very unsafe
    safe_mask = vlh["vlh04"].isin([1, 2])
    vlh_safe = vlh[safe_mask]
    
    # Merge with nna to find households with non-ag business ownership
    # nna['nna01']: 1: Yes, 2: No
    nna_own = nna[nna["nna01"] == 1]
    
    # Merge vlh_safe with nna_own on 'folio'
    merged = pd.merge(vlh_safe, nna_own, on="folio", how="inner")
    
    # Get household IDs that meet criteria
    households_ids = merged["folio"].unique()
    
    # Filter portad for these households
    portad_filtered = portad[portad["folio"].isin(households_ids)]
    
    # Merge with vlh to get 'vlh18a' (total times entered/rob house/business/parcel since 2005)
    merged_full = pd.merge(portad_filtered, vlh, on="folio", how="inner")
    
    # Filter for households with 'vlh18a' not null
    merged_full = merged_full[merged_full["vlh18a"].notna()]
    
    # Calculate the national average of 'vlh18a' for this group
    national_avg = merged_full["vlh18a"].mean()
    
    # Count households per state
    state_counts = merged_full.groupby("ent").size()
    # Filter states with at least 50 households
    valid_states = state_counts[state_counts >= 50].index
    
    # Filter merged_full for these states
    filtered_states = merged_full[merged_full["ent"].isin(valid_states)]
    
    # Group by state and calculate mean 'vlh18a' and count
    result = (
        filtered_states.groupby("ent")
        .agg(
            average_breakins=("vlh18a", "mean"),
            household_count=("folio", "nunique")
        )
        .reset_index()
    )
    
    # Order from highest to lowest average
    result = result.sort_values(by="average_breakins", ascending=False)
    
    # Map 'ent' codes to state names for clarity
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
    result = result[["state", "average_breakins", "household_count"]]
    return result