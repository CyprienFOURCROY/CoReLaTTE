def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    
    # Filter households where a member owns/shares a non-agricultural business
    nna_owned = nna[nna["nna01"] == 1][["folio"]]
    
    # Filter households with debts in last 12 months
    crh_debt = crh[crh["crh02_1"] == 1]
    # For these households, get total debts and payments
    crh_debt = crh_debt[["folio", "crh04_2", "crh03_2"]]
    crh_debt = crh_debt.dropna(subset=["crh04_2", "crh03_2"])
    
    # Calculate ratio of payment to debt for each household
    crh_debt = crh_debt[crh_debt["crh04_2"] != 0]
    crh_debt["payment_debt_ratio"] = crh_debt["crh03_2"] / crh_debt["crh04_2"]
    
    # Filter households where payments > debts
    households_payments_exceed_debt = crh_debt[crh_debt["payment_debt_ratio"] > 1]
    
    # Compute average borrowed amount among indebted households
    avg_borrowed = households_payments_exceed_debt["crh04_2"].mean()
    
    # Filter households where payment > borrowed amount and payment > average borrowed
    filtered = households_payments_exceed_debt[
        (households_payments_exceed_debt["crh03_2"] > households_payments_exceed_debt["crh04_2"]) &
        (households_payments_exceed_debt["crh03_2"] > avg_borrowed)
    ]
    
    # Join with portad to get state info
    result = filtered.merge(portad[["folio", "ent"]], on="folio", how="inner")
    
    # Count households per state
    state_counts = result.groupby("ent").size().reset_index(name="household_count")
    
    # Map state codes to state names (optional, only if needed)
    # For ranking, only codes are sufficient
    # Rank states by household count
    state_counts = state_counts.sort_values(by="household_count", ascending=False).reset_index(drop=True)
    
    # Return as DataFrame with rank
    return state_counts