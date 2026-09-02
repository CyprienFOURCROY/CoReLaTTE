def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    vlh = tables["ii_vlh"]
    
    # Filter households in Oaxaca (20) and Puebla (21)
    filtered_portad = portad[portad["ent"].isin([20, 21])]
    
    # Filter households with age >= 25
    filtered_portad = filtered_portad[filtered_portad["edad"] >= 25]
    
    # Merge with crh on 'folio'
    merged_crh = pd.merge(filtered_portad, crh, on="folio", how="inner")
    
    # Filter households with total debt (crh04_2) >= 5000 pesos and not missing
    debt_mask = (merged_crh["crh04_2"].notna()) & (merged_crh["crh04_2"] >= 5000)
    filtered_debt = merged_crh[debt_mask]
    
    # Merge with vlh on 'folio'
    merged_vlh = pd.merge(filtered_debt, vlh, on="folio", how="inner")
    
    # Filter households where 'vlh04' (feel safe at home) is not missing
    safe_mask = merged_vlh["vlh04"].notna()
    final_df = merged_vlh[safe_mask]
    
    # Group by 'ent' (state)
    result = final_df.groupby("ent").agg(
        avg_feel_safe=("vlh04", "mean"),
        avg_total_debt=("crh04_2", "mean"),
        household_count=("folio", "nunique")
    ).reset_index()
    
    # Map 'ent' codes to state names for clarity
    ent_map = {
        20: "Oaxaca",
        21: "Puebla"
    }
    result["state"] = result["ent"].map(ent_map)
    
    # Order from safest (lowest 'vlh04') to least safe (highest)
    result = result.sort_values(by="avg_feel_safe")
    
    # Select relevant columns
    result = result[["state", "avg_feel_safe", "avg_total_debt", "household_count"]]
    
    return result