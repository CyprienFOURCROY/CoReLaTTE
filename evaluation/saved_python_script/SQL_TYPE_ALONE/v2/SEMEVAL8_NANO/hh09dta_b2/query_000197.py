def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    inr = tables["ii_inr"]
    
    # Filter for Oaxaca (ent == 15) and land use for farming (su01 == 1)
    oaxaca_land_use = portad[
        (portad["ent"] == 15) & (portad["folio"].isin(su["folio"])) & (su["su01"] == 1)
    ][["folio"]]
    
    # Merge with inr to get expenses
    merged = pd.merge(oaxaca_land_use, inr, on="folio", how="left")
    
    # Filter for land-using households with non-missing fertilizer expenses
    land_fertilizer = merged[
        (merged["su231"].notna()) & (merged["su231"] > 0)
    ][["folio", "su231"]]
    
    # Calculate average fertilizer expense among all land-using households
    avg_fertilizer = land_fertilizer["su231"].mean()
    
    # Filter households with expenses above the average
    above_avg = land_fertilizer[land_fertilizer["su231"] > avg_fertilizer]
    
    # Sort from highest to lowest expense
    result = above_avg.sort_values(by="su231", ascending=False)[["folio", "su231"]]
    
    # Rename columns for clarity
    result = result.rename(columns={"su231": "chemical_fertilizer_expense"})
    
    return result.reset_index(drop=True)