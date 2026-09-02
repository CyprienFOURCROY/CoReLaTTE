def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    se = tables["ii_se"]
    nna = tables["ii_nna"]
    inr = tables["ii_inr"]
    se_enriched = tables["ii_se_enriched"]
    inr_enriched = tables["ii_inr_enriched"]
    nna_enriched = tables["ii_nna_enriched"]
    
    # Filter portad for age >= 30
    portad_filtered = portad[portad["edad"] >= 30]
    
    # Merge portad with vlh on 'folio'
    merged = pd.merge(portad_filtered, vlh, on="folio", how="inner")
    # Merge with se on 'folio'
    merged = pd.merge(merged, se, on="folio", how="inner")
    
    # Merge with inr_enriched on 'folio'
    merged = pd.merge(merged, inr_enriched[["folio", "inr02f"]], on="folio", how="left")
    
    # Filter for produce/sell crafts in last 12 months
    crafts_mask = merged["inr02f"] == 1
    merged_crafts = merged[crafts_mask]
    
    # Filter for feeling safe at home ('vlh04' column)
    # 'vlh04' values: 1: Very safe, 2: Safe
    safe_mask = merged_crafts["vlh04"].isin([1, 2])
    merged_safe = merged_crafts[safe_mask]
    
    # Count total respondents per state ('ent' column)
    # 'ent' codes: 2: Baja California, 3: Baja California Sur, etc.
    counts = (
        merged_safe.groupby("ent")
        .size()
        .reset_index(name="respondent_count")
    )
    
    # Calculate overall average across states
    overall_avg = counts["respondent_count"].mean()
    
    # Filter states with at least the average number of respondents
    states_above_avg = counts[counts["respondent_count"] >= overall_avg]
    
    # Map 'ent' codes to state names for clarity (optional)
    ent_map = {
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
    states_above_avg["state"] = states_above_avg["ent"].map(ent_map)
    
    # Sort from highest to lowest
    result = states_above_avg.sort_values(by="respondent_count", ascending=False)[["state", "respondent_count"]]
    
    return result.reset_index(drop=True)