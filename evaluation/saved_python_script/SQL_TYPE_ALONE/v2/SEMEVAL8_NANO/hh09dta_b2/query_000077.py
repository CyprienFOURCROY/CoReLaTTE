def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    vlh = tables["ii_vlh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge households with crh on 'folio'
    merged_crh = pd.merge(oaxaca_households, crh, on="folio", how="inner")
    
    # Filter households that reported a payment in last 12 months (crh03_1 == 1)
    paid_last_12_months = merged_crh[merged_crh["crh03_1"] == 1]
    
    # Calculate overall average amount paid in pesos
    # Exclude NaN values
    overall_avg_paid = paid_last_12_months["crh03_2"].dropna().mean()
    
    # Filter households with amounts greater than the overall average
    high_payments = paid_last_12_months[
        (paid_last_12_months["crh03_2"] > overall_avg_paid)
    ]
    
    # Select Household ID ('folio') and amount paid ('crh03_2')
    result = high_payments[["folio", "crh03_2"]]
    
    # Drop NaN amounts
    result = result.dropna(subset=["crh03_2"])
    
    # Sort from highest to lowest amount
    result_sorted = result.sort_values(by="crh03_2", ascending=False).reset_index(drop=True)
    
    return result_sorted