def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Filter households with at least one adult (edad >= 18)
    households_with_adults = oaxaca_households[oaxaca_households["edad"] >= 18]
    
    # Filter households where a member owns/shares a non-ag business (nna01 == 1)
    nna_owned = nna[nna["nna01"] == 1]
    
    # Merge to get households with non-ag business owners
    households_with_business = pd.merge(
        households_with_adults,
        nna_owned[["folio"]],
        on="folio",
        how="inner"
    )
    
    # Filter households that both owed and paid on credit/loans in last 12 months
    crh_filtered = crh[
        (crh["folio"].isin(households_with_business["folio"])) &
        (crh["crh02_1"].isin([1,8])) &  # Owed credit/loans
        (crh["crh03_1"].isin([1,8]))    # Paid in last 12 months
    ]
    
    # For each household, get total owed and paid amounts
    owed_paid = crh_filtered.groupby("folio").agg({
        "crh02_2": "mean",  # Average amount owed
        "crh03_2": "mean"   # Average amount paid
    }).reset_index()
    
    # Filter households where both owed and paid amounts are available
    owed_paid = owed_paid.dropna(subset=["crh02_2", "crh03_2"])
    
    # Calculate the average amount paid across these households
    avg_paid = owed_paid["crh03_2"].mean()
    
    # Filter households that paid more than the group average
    households_above_avg = owed_paid[owed_paid["crh03_2"] > avg_paid]
    
    # Select relevant columns and sort by amount paid descending
    result = households_above_avg[["folio", "crh02_2", "crh03_2"]]
    result = result.rename(columns={"crh02_2": "amount_owed", "crh03_2": "amount_paid"})
    result = result.sort_values(by="amount_paid", ascending=False).reset_index(drop=True)
    
    return result