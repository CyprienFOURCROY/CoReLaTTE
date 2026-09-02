def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]
    
    # Filter households that use land for farming (su01 == 1)
    land_farming = df_ah[df_ah["su01"] == 1]
    
    # Filter households that own a motor vehicle (ah03d == 1)
    households_with_vehicle = land_farming[land_farming["ah03d"] == 1]
    
    # Get list of household IDs (folio) that meet both conditions
    household_ids = households_with_vehicle["folio"]
    
    # Filter ii_inr for these households
    df_inr_filtered = df_inr[df_inr["folio"].isin(household_ids)]
    
    # Select seed expense column
    seed_expenses = df_inr_filtered["su234"]
    
    # Filter for positive seed expenses
    positive_seed_expenses = seed_expenses[seed_expenses > 0]
    
    # Calculate average seed expense across all positive seed expenses
    avg_seed_expense = positive_seed_expenses.mean()
    
    # Filter households with seed expense greater than the average
    households_above_avg = df_inr_filtered[ df_inr_filtered["su234"] > avg_seed_expense ]
    
    # Select folio and seed expense, order from highest to lowest
    result = households_above_avg[["folio", "su234"]].sort_values(by="su234", ascending=False)
    
    # Return as DataFrame
    return result.reset_index(drop=True)