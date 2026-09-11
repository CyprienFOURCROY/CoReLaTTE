def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    in_table = tables["ii_in"]
    nna = tables["ii_nna"]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca_portad = portad[portad["ent"] == 15]
    
    # Merge portad with in_table on 'folio'
    merged = pd.merge(oaxaca_portad, in_table, on="folio", how="inner")
    
    # Filter for households with positive amount from 'in02a10' (Other Government Program)
    # and amount > Oaxaca average among such recipients
    # First, filter for positive amounts
    positive_in02a10 = merged[merged["in02a10"] > 0]
    
    # Compute average of 'in02a10' among recipients
    avg_in02a10 = positive_in02a10["in02a10"].mean()
    
    # Filter for households with 'in02a10' > average
    high_in02a10 = positive_in02a10[positive_in02a10["in02a10"] > avg_in02a10]
    
    # Merge with ah to get ownership info
    merged_ah = pd.merge(high_in02a10, ah, on=["folio", "ls"], how="left")
    
    # Merge with nna to get non-ag business ownership
    merged_final = pd.merge(merged_ah, nna[["folio", "nna01"]], on="folio", how="left")
    
    # Filter for households in Oaxaca (already filtered) and with 'nna01' not null
    # (assuming all households in merged_final are in Oaxaca)
    # Group by ownership of non-ag business
    group = merged_final.groupby("nna01")["edad"].mean().reset_index()
    
    # Map 'nna01' to descriptive labels
    group["nna01"] = group["nna01"].map({1: "Owns/shares non-ag business", 2: "Does not own/share non-ag business"})
    
    # Prepare result DataFrame
    result = group.rename(columns={"edad": "average_household_size"})
    
    return result