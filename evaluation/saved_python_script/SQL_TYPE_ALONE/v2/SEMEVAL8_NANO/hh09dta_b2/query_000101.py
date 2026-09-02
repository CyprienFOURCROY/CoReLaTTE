def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]
    
    # Filter households that own/share non-agricultural business (nna01 == 1)
    nna_owned = df_nna[df_nna["nna01"] == 1][["folio", "nna02"]]
    
    # Merge with portad to get state info
    portad_nna = pd.merge(nna_owned, df_portad[["folio", "ent"]], on="folio", how="inner")
    
    # Filter households that do NOT use any plot/land for farming (su01 == 3)
    su_no_land = df_su[df_su["su01"] == 3][["folio"]]
    
    # Merge with households owning/sharing non-ag business
    households = pd.merge(portad_nna, su_no_land, on="folio", how="inner")
    
    # Filter households with last 12 months number of non-ag businesses > 1.5
    households_filtered = households[households["nna02"] > 1.5]
    
    # Group by state and count households
    result = (
        households_filtered
        .groupby("ent")
        .size()
        .reset_index(name="household_count")
    )
    
    # Filter states with average >= 1.5 (since groupby count is households, and each household has at least 1 non-ag business)
    # But since we want average number of non-ag businesses per household, we need to compute mean of nna02 per state
    # So, instead, group by state and compute mean of nna02
    mean_nna = (
        households_filtered
        .groupby("ent")["nna02"]
        .mean()
        .reset_index()
    )
    
    # Filter states with mean >= 1.5
    states_result = mean_nna[mean_nna["nna02"] >= 1.5]
    
    # For each state, count households that meet criteria
    counts = (
        households_filtered[["ent", "folio"]]
        .drop_duplicates()
        .groupby("ent")
        .size()
        .reset_index(name="household_count")
    )
    
    # Merge counts with states_result to get final output
    final_df = pd.merge(states_result, counts, on="ent")
    
    # Map state codes to labels if needed (optional, not specified)
    # Return final DataFrame with state code and count
    return final_df.rename(columns={"ent": "state_code", "nna02": "average_non_ag_businesses", "household_count": "households_count"})