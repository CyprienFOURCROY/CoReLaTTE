def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    vlh = tables["ii_vlh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge with crh on 'folio'
    merged = pd.merge(oaxaca_households, crh, on="folio", how="inner")
    
    # Filter households with positive total debt (crh04_2 > 0)
    debt_positive = merged[merged["crh04_2"] > 0]
    
    # Merge with vlh on 'folio'
    merged_vlh = pd.merge(debt_positive, vlh, on="folio", how="inner")
    
    # Conditions:
    # 1. Feel unsafe or very unsafe at home: vlh04 in [3,4]
    unsafe_mask = merged_vlh["vlh04"].isin([3,4])
    
    # 2. Disagree or completely disagree that locality is close-knit: vlh01k in [3,4]
    close_knit_mask = merged_vlh["vlh01k"].isin([3,4])
    
    # Apply both conditions
    final_mask = unsafe_mask & close_knit_mask
    filtered = merged_vlh[final_mask]
    
    # Calculate average amount in pesos
    avg_amount = filtered["crh04_2"].mean()
    
    # Count households meeting the condition
    count_households = filtered["folio"].nunique()
    
    # Return results in a DataFrame
    return pd.DataFrame({
        "average_amount": [avg_amount],
        "household_count": [count_households]
    })