def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    in_table = tables["ii_in"]
    
    # Filter households in Oaxaca (ent == 15)
    oaxaca_households = portad[portad["ent"] == 15]
    
    # Merge with vlh and in tables on 'folio'
    merged = oaxaca_households.merge(vlh, on="folio", how="left").merge(in_table, on="folio", how="left")
    
    # Filter households that feel very safe or safe at home
    safety_mask = merged["vlh04"].isin([1, 2])
    
    # Filter households where people are willing to help neighbors
    help_mask = merged["vlh01l"].isin([1, 2, 3, 4])  # All responses except DK (8), so include 1-4
    
    # Combine safety and help masks
    filtered = merged[safety_mask & help_mask]
    
    # Filter households with positive receipt from 'in02a10' (amount > 0)
    # 'in02a10' is the amount received directly from Other Government Program
    positive_receipt_mask = filtered["in02a10"] > 0
    
    # Calculate the average among households with positive receipts
    if positive_receipt_mask.any():
        avg_amount = filtered.loc[positive_receipt_mask, "in02a10"].mean()
    else:
        avg_amount = 0
    
    # Filter households with 'in02a10' above the average
    above_avg_mask = filtered["in02a10"] > avg_amount
    
    # Count households satisfying all conditions
    count = filtered.loc[above_avg_mask].shape[0]
    
    return pd.DataFrame({"count": [count]})