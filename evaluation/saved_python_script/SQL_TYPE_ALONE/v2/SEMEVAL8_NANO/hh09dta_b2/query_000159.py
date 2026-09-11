def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    inr = tables["ii_inr"]
    
    # Filter households with total debts plus interests reported (crh04_1 != nan)
    crh_debt = crh[crh["crh04_1"].notna()]
    
    # Merge with portad to get age info
    merged = crh_debt.merge(portad, on="folio", how="inner")
    
    # Compute the oldest interviewed member's age per household
    # For each household, find the maximum 'edad' among members
    household_oldest_age = (
        merged.groupby("folio")["edad"]
        .max()
        .reset_index()
        .rename(columns={"edad": "oldest_age"})
    )
    
    # Calculate the average oldest age across these households
    avg_oldest_age = household_oldest_age["oldest_age"].mean()
    
    # Merge back to get household info
    household_info = household_oldest_age
    
    # Merge with inr to identify households that produce/sell dairy products
    inr_dairy = inr[["folio", "inr02a"]]
    household_info = household_info.merge(inr_dairy, on="folio", how="left")
    
    # Fill missing inr02a with 3 (assumed 'No') if any
    household_info["inr02a"] = household_info["inr02a"].fillna(3)
    
    # Create a flag for production/selling dairy (Yes=1, No=0)
    household_info["produces_dairy"] = household_info["inr02a"].apply(lambda x: 1 if x == 1 else 0)
    
    # Count households with oldest member >= average oldest age, broken down by dairy production
    result = (
        household_info.groupby("produces_dairy")
        .apply(lambda df: (df["oldest_age"] >= avg_oldest_age).sum())
        .reset_index(name="count")
    )
    
    # Map produces_dairy to descriptive label
    result["dairy_production"] = result["produces_dairy"].map({1: "Yes", 0: "No"})
    
    # Select relevant columns
    result = result[["dairy_production", "count"]]
    
    return result