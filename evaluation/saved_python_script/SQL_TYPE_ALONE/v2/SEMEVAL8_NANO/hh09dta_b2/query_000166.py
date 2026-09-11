def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    crh = tables["ii_crh"]
    se = tables["ii_se"]
    
    # Filter households who answered 'No' to knowing a family or friend robbed in last 12 months
    # 'se02fa_1' indicates if they know someone robbed in last 12 months
    # '2' means 'Did not know' (No)
    no_rob_last12 = se[se["se02fa_1"] == 2][["folio"]]
    
    # Merge with 'vlh' to get 'vlh03' (age in which they arrived in house) and 'vlh04' (feel safe at home)
    merged = no_rob_last12.merge(vlh, on="folio", how="left")
    
    # Filter households where 'vlh04' (feel safe at home) is >= 3 (Unsafe/Very unsafe)
    filtered = merged[merged["vlh04"] >= 3]
    
    # Merge with 'portad' to get 'ent' (state)
    filtered = filtered.merge(portad[["folio", "ent"]], on="folio", how="left")
    
    # Map 'ent' codes to state names for clarity
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
    filtered["state"] = filtered["ent"].map(ent_map)
    
    # Calculate the national average of 'vlh04' for this group
    national_avg = filtered["vlh04"].mean()
    
    # Group by state to get mean 'vlh04' and household count
    state_stats = (
        filtered.groupby("state")
        .agg(
            avg_safe_score=("vlh04", "mean"),
            household_count=("folio", "count")
        )
        .reset_index()
    )
    
    # Filter states where average 'vlh04' >= 3 and above the national average
    result = state_stats[
        (state_stats["avg_safe_score"] >= 3) & 
        (state_stats["avg_safe_score"] > national_avg)
    ]
    
    # Rank from highest (least safe) to lowest
    result = result.sort_values(by="avg_safe_score", ascending=False).reset_index(drop=True)
    
    return result