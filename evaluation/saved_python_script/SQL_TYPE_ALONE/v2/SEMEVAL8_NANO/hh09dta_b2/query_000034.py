def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_nna = tables["ii_nna"]
    
    # Filter households that own/share a non-agricultural business
    nna_owners = df_nna[df_nna["nna01"] == 1][["folio"]]
    
    # Merge with household info to get relevant households
    households = nna_owners
    
    # Merge with ii_in to get info about receipt of Liconsa, Pronjag, and participation in Other Government Program
    df_in_filtered = df_in[["folio", "in03a", "in03b", "in03c_1", "in02a10"]]
    households_in = households.merge(df_in_filtered, on="folio", how="inner")
    
    # Filter households that received Liconsa milk in last 12 months (in03a == 1)
    # Did not receive Pronjag (in03b != 1)
    # Participated in and received income from Other Government Program (in03c_1 == 1)
    households_filtered = households_in[
        (households_in["in03a"] == 1) &
        (households_in["in03b"] != 1) &
        (households_in["in03c_1"] == 1)
    ].copy()
    
    # Calculate the overall average of directly received amount from the program (in02a10)
    overall_mean = households_filtered["in02a10"].mean()
    
    # Filter households with directly received amount above the overall average
    households_above_avg = households_filtered[households_filtered["in02a10"] > overall_mean]
    
    # Count total households meeting criteria per state
    total_households_per_state = (
        households_above_avg.groupby("ent")
        .size()
        .reset_index(name="total_households")
    )
    
    # Merge with original to get household IDs for counting debts
    households_ids = households_above_avg[["folio", "ent"]]
    df_in_debts = df_in[["folio", "crh02_1", "crh02_2"]]
    households_debts = households_ids.merge(df_in_debts, on="folio", how="left")
    
    # Filter households that paid any money on debts/loans in the last 12 months (crh02_1 == 1)
    households_paid_debts = households_debts[households_debts["crh02_1"] == 1]
    
    # Count households paying debts per state
    debts_count_per_state = (
        households_paid_debts.groupby("ent")
        .size()
        .reset_index(name="households_paid_debts")
    )
    
    # Merge counts
    result = total_households_per_state.merge(
        debts_count_per_state,
        on="ent",
        how="left"
    )
    
    # Fill NaN with 0 for households_paid_debts
    result["households_paid_debts"] = result["households_paid_debts"].fillna(0).astype(int)
    
    # Map 'ent' to state names for clarity (optional, but not required)
    # Create final DataFrame with ent, total_households, households_paid_debts
    return result[['ent', 'total_households', 'households_paid_debts']]