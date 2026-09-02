def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    nna = tables["ii_nna"]
    su = tables["ii_su"]
    inr = tables["ii_inr"]
    
    # Filter households that use land for farming (su01 == 1)
    land_use = su[su["su01"] == 1]
    
    # Merge land_use with portad to get household info
    land_use = land_use.merge(portad[["folio", "rel"]], on="folio", how="inner")
    
    # Filter households that did not lose total crop in last 5 years (se01e == 3)
    se_crop_loss = se[se["se01e"] == 3]
    
    # Get household IDs that did NOT lose total crop
    households_no_loss = se_crop_loss["folio"].unique()
    
    # Filter land-using households that did not lose total crop
    households_no_loss_df = land_use[land_use["folio"].isin(households_no_loss)]
    
    # Get seed expenses for these households
    seed_expenses = inr[inr["folio"].isin(households_no_loss_df["folio"])]
    seed_expenses = seed_expenses[["folio", "su233"]]
    
    # Calculate average seed expense among households that did not lose total crop
    avg_seed_expense = seed_expenses["su233"].mean()
    
    # Filter land-using households with seed expense > average
    households_high_seed = seed_expenses[seed_expenses["su233"] > avg_seed_expense]
    
    # Merge with portad to get household IDs and expenses
    result = households_high_seed.merge(portad[["folio", "ent"]], on="folio", how="left")
    
    # Select household ID and seed expense, sort from highest to lowest
    result = result[["folio", "su233"]].sort_values(by="su233", ascending=False).reset_index(drop=True)
    
    return result