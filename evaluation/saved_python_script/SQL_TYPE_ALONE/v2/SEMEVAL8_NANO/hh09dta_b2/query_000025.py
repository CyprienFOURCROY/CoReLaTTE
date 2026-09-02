def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    su = tables["ii_su"]
    vlh = tables["ii_vlh"]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca = portad[portad["ent"] == 15]
    
    # Merge with nna to get 'nna02' (last 12 months non-ag business owned/shared)
    merged = pd.merge(oaxaca, nna, on="folio", how="left")
    
    # Merge with su to get 'su231' (expenses in chemical fertilizer)
    merged = pd.merge(merged, su[["folio", "su231"]], on="folio", how="left")
    
    # Merge with vlh to get 'vlh01d' (district conflicts neighbors) or other relevant info if needed
    # Not directly needed for the calculation, but included for completeness
    merged = pd.merge(merged, vlh[["folio", "vlh01d"]], on="folio", how="left")
    
    # Filter for households in Oaxaca
    oaxaca_households = merged.copy()
    
    # Drop rows with missing 'nna02' or 'su231' or 'vlh01d' if any
    oaxaca_households = oaxaca_households.dropna(subset=["nna02", "su231"])
    
    # Calculate the state average of 'su231' (expenses in chemical fertilizer)
    state_avg_expense = oaxaca_households["su231"].mean()
    
    # Filter households with 'su231' above the state average
    above_avg = oaxaca_households[oaxaca_households["su231"] > state_avg_expense]
    
    # Calculate the average worker expense among these households
    avg_worker_expense = above_avg["su231"].mean()
    
    # Group by 'nna02' (last 12 months non-ag business owned/shares)
    # and by whether they know a family or friend robbed in last 5 years ('vlh08a' indicates if they know someone robbed)
    # First, merge with vlh to get 'vlh08a' (know someone robbed in last 5 years)
    merged_full = pd.merge(above_avg, vlh[["folio", "vlh08a"]], on="folio", how="left")
    
    # Drop rows with missing 'vlh08a'
    merged_full = merged_full.dropna(subset=["vlh08a"])
    
    # Convert 'vlh08a' to boolean for clarity
    merged_full["knows_robbed"] = merged_full["vlh08a"] == 1
    
    # Group by 'nna02' and 'knows_robbed' and count households
    result = (
        merged_full
        .groupby(["nna02", "knows_robbed"])
        .size()
        .reset_index(name="household_count")
    )
    
    # Prepare final output
    output = pd.DataFrame(
        {
            "average_worker_expense": [avg_worker_expense],
            "nna02": result["nna02"],
            "knows_robbed": result["knows_robbed"],
            "household_count": result["household_count"]
        }
    )
    
    return output