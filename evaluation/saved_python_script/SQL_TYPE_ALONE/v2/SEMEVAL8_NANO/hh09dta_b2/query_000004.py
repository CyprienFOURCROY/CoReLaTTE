def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_vlh = tables["ii_vlh"]
    
    # Filter households that use a plot/land for farming (su01 == 1)
    df_su_farming = df_su[df_su["su01"] == 1]
    
    # Merge with portad to get 'ent' (state) info
    merged = pd.merge(df_su_farming[["folio"]], df_portad[["folio", "ent"]], on="folio", how="inner")
    
    # Merge with vlh to get 'vlh04' (feel safe at home)
    merged = pd.merge(merged, df_vlh[["folio", "vlh04"]], on="folio", how="inner")
    
    # Filter out households with less than 2 households per state
    counts = merged["ent"].value_counts()
    valid_states = counts[counts >= 2].index
    filtered = merged[merged["ent"].isin(valid_states)]
    
    # Calculate mean 'vlh04' per state
    mean_scores = (
        filtered.groupby("ent")["vlh04"]
        .mean()
        .reset_index()
    )
    
    # Map 'ent' codes to state names for clarity (optional, not required)
    state_mapping = {
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
    mean_scores["state"] = mean_scores["ent"].map(state_mapping)
    
    # Select top 5 states with lowest average 'vlh04'
    result = (
        mean_scores
        .sort_values(by="vlh04", ascending=True)
        .head(5)
        .reset_index(drop=True)
    )
    
    return result[["state", "vlh04"]]