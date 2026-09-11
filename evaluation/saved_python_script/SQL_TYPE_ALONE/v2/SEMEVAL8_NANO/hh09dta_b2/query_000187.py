def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_su = tables["ii_su"]
    df_su_enriched = tables["ii_su_enriched"]
    df_in_enriched = tables["ii_in_enriched"]
    
    # Filter households where a member uses land for farming
    land_use_mask = df_su_enriched["su01"] == 1
    households_with_land = df_su_enriched.loc[land_use_mask, "folio"].unique()
    
    # Filter households that participated in an Other Government Help in last 12 months
    other_gov_mask = df_in_enriched["in03c_1"] == 1
    households_other_gov = df_in_enriched.loc[other_gov_mask, "folio"]
    
    # Find intersection: households with land use AND participated in other government help
    target_households = set(households_with_land).intersection(set(households_other_gov))
    
    # Filter in data for these households
    df_in_filtered = df_in[df_in["folio"].isin(target_households)]
    
    # Filter for households that received a positive direct payment > 0
    # The relevant amount columns are in columns like in02a2, in02a3, etc.
    amount_columns = [
        "in02a2", "in02a3", "in02a5", "in02a6", "in02a7", "in02a9", "in02a10", "in02a11", "in02a12", "in02a13"
    ]
    # Filter for positive amounts
    df_amounts = df_in_filtered[amount_columns]
    # Replace NaN with 0 for comparison
    df_amounts_filled = df_amounts.fillna(0)
    # Create a mask for positive amounts
    positive_mask = (df_amounts_filled > 0).any(axis=1)
    df_positive_payments = df_in_filtered[positive_mask]
    
    # For these households, find the maximum amount received from the relevant columns
    df_positive_payments_amounts = df_positive_payments[amount_columns]
    df_positive_payments_amounts_filled = df_positive_payments_amounts.fillna(0)
    max_amounts = df_positive_payments_amounts_filled.max(axis=1)
    
    # Calculate the average of these maximum amounts
    average_amount = max_amounts.mean()
    
    # Select households with max amount > average
    households_above_avg_mask = max_amounts > average_amount
    result_df = df_positive_payments[households_above_avg_mask][["folio", "in02a2"]]
    
    # Rename column for clarity
    result_df = result_df.rename(columns={"in02a2": "amount_received"})
    
    # Return only folio and amount_received
    return result_df.reset_index(drop=True)