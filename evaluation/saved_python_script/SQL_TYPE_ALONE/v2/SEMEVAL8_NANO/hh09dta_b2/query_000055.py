def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    nna = tables["ii_nna"]
    ah = tables["ii_ah"]
    
    # Filter households with at least one adult (edad >= 18)
    households_adults = portad[portad["edad"] >= 18]
    
    # Filter households that own/share a non-agricultural business
    nna_filtered = nna[nna["nna01"] == 1]
    households_with_nna = households_adults[households_adults["folio"].isin(nna_filtered["folio"])]
    
    # Filter households that did not incur debts in last 12 months (crh02_1 == 2)
    crh_filtered = crh[crh["crh02_1"] == 2]
    households_no_debt = households_with_nna[households_with_nna["folio"].isin(crh_filtered["folio"])]
    
    # Filter households that reported a value for wash machine/stove (ah04f_2 not null and not 8)
    ah_filtered = ah[
        (ah["ah04f_2"].notnull()) & (ah["ah04f_2"] != 8)
    ]
    households_with_assets = households_no_debt[
        households_no_debt["folio"].isin(ah_filtered["folio"])
    ]
    
    # Merge to get all relevant data
    merged = households_with_assets.merge(ah, on=["folio"], how="left")
    merged = merged.merge(crh, on=["folio"], how="left")
    merged = merged.merge(nna, on=["folio"], how="left")
    
    # Filter for households with at least one adult (already filtered), owner/share non-ag (nna01==1),
    # no debts last 12 months (crh02_1==2), and report value for wash machine/stove (ah04f_2 not null and !=8)
    filtered = merged[
        (merged["edad"] >= 18) &
        (merged["nna01"] == 1) &
        (merged["crh02_1"] == 2) &
        (merged["ah04f_2"].notnull()) &
        (merged["ah04f_2"] != 8)
    ]
    
    # For each household, get the value of wash machine/stove assets (ah04f_2)
    # Some households may have multiple individuals; group by folio and take the first non-null value
    household_assets = filtered.groupby("folio").agg({
        "ah04f_2": "first",
        "ent": "first"
    }).reset_index()
    
    # Calculate the average total household value of wash machine/stove assets per household
    # Only consider households with a reported value
    household_assets = household_assets[household_assets["ah04f_2"].notnull()]
    
    # Compute the national average
    national_avg = household_assets["ah04f_2"].mean()
    
    # Get households with asset value above the national average
    above_avg = household_assets[household_assets["ah04f_2"] > national_avg]
    
    # Merge with portad to get state info
    result = above_avg.merge(portad[["folio", "ent"]], on="folio", how="left")
    
    # Group by state (ent) and compute mean asset value
    state_avg = result.groupby("ent")["ah04f_2"].mean().reset_index()
    
    # Map state codes to state names (from metadata)
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
    state_avg["state"] = state_avg["ent"].map(state_mapping)
    
    # Rank states from highest to lowest average
    ranked = state_avg.sort_values(by="ah04f_2", ascending=False)
    
    # Select only state name and average value
    result_df = ranked[["state", "ah04f_2"]].reset_index(drop=True)
    
    return result_df