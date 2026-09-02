def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_enriched = tables["ii_ah_enriched"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20]
    
    # Filter households that own electronic device (ah04e_1 == 1)
    households_with_electronic = oaxaca_households[
        oaxaca_households["folio"].isin(
            df_enriched[df_enriched["ah04e_1"] == 1]["folio"]
        )
    ]
    
    # Get household IDs in Oaxaca with electronic device
    oaxaca_folios = households_with_electronic["folio"]
    
    # Filter inr table for these households
    inr_filtered = df_inr[df_inr["folio"].isin(oaxaca_folios)]
    
    # Filter for households that reported owing money (crh02_1 == 1)
    households_with_debt = inr_filtered[inr_filtered["crh02_1"] == 1]
    
    # Filter for those who made payments in last 12 months (crh03_1 == 1)
    households_paid_last_12_months = households_with_debt[households_with_debt["crh03_1"] == 1]
    
    # Calculate the average amount paid in pesos
    # Filter out NaN in crh03_2
    valid_payments = households_paid_last_12_months[~households_paid_last_12_months["crh03_2"].isna()]
    if valid_payments.empty:
        return pd.DataFrame(columns=["folio", "amount_paid"])
    avg_amount = valid_payments["crh03_2"].mean()
    
    # Find households that paid more than the average
    high_payers = valid_payments[valid_payments["crh03_2"] > avg_amount]
    
    # Select household ID and amount paid, sorted from highest to lowest
    result = high_payers[["folio", "crh03_2"]].sort_values(by="crh03_2", ascending=False)
    result = result.rename(columns={"crh03_2": "amount_paid"})
    
    return result.reset_index(drop=True)