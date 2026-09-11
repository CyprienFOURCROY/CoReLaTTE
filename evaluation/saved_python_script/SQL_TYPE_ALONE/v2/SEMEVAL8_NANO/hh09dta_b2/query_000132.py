def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]
    
    # Filter households that use a plot/land for farming
    # su01: 1 means Yes
    households_with_land = df_su[df_su["su01"] == 1][["folio"]]
    
    # Filter households that have bank savings
    # crh01_1b: 2 means Bank
    df_crh = tables["ii_crh"]
    households_with_bank_savings = df_crh[df_crh["crh01_1b"] == 2][["folio"]]
    
    # Find households that satisfy both conditions
    households_both = pd.merge(households_with_land, households_with_bank_savings, on="folio")
    
    # Filter inr for these households
    df_inr_filtered = df_inr[df_inr["folio"].isin(households_both["folio"])]
    
    # Calculate average spent on workers (crh04_2: total debts + interests in pesos)
    # Filter out missing values
    df_inr_filtered = df_inr_filtered.dropna(subset=["crh04_2"])
    if df_inr_filtered.empty:
        # If no data, return empty DataFrame
        return pd.DataFrame(columns=["Household ID", "Amount"])
    
    avg_spent_on_workers = df_inr_filtered["crh04_2"].mean()
    
    # Find households that spent more than the average
    households_high_spenders = df_inr_filtered[df_inr_filtered["crh04_2"] > avg_spent_on_workers]
    
    # Select household ID and amount spent
    result = households_high_spenders[["folio", "crh04_2"]]
    result = result.rename(columns={"folio": "Household ID", "crh04_2": "Amount"})
    
    # Sort from highest to lowest
    result = result.sort_values(by="Amount", ascending=False).reset_index(drop=True)
    
    return result