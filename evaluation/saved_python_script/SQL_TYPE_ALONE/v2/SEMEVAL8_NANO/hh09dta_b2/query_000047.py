def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    nna = tables["ii_nna"]
    ah = tables["ii_ah"]
    inr = tables["ii_inr"]
    
    # Filter households with at least one member owning financial assets/afores
    ah_fin_assets = ah[ah["ah03h"] == 1][["folio"]].drop_duplicates()
    
    # Filter households that own/share non-agricultural business
    nna_non_ag = nna[nna["nna01"] == 1][["folio"]].drop_duplicates()
    
    # Merge to get households with financial assets and non-ag business ownership
    households_with_assets = pd.merge(ah_fin_assets, nna_non_ag, on="folio", how="inner")
    
    # Get total times entered/rob since 2005 for these households
    vlh_since_2005 = vlh[
        (vlh["vlh12a_a"] == 1) | (vlh["vlh12a_b"] == 2) | (vlh["vlh12a_c"] == 3)
    ][["folio", "vlh13a"]]
    
    # For households with assets, get their total times since 2005
    households_with_assets_times = pd.merge(households_with_assets, vlh_since_2005, on="folio", how="left")
    
    # Fill NaN with 0 for households with no data
    households_with_assets_times["vlh13a"] = households_with_assets_times["vlh13a"].fillna(0)
    
    # Compute average total times since 2005 for households with assets
    avg_times = households_with_assets_times["vlh13a"].mean()
    
    # For households without non-ag business ownership, get their total times since 2005
    households_without_nna = nna[nna["nna01"] != 1][["folio"]].drop_duplicates()
    vlh_without_nna = vlh[
        (vlh["vlh12a_a"] == 1) | (vlh["vlh12a_b"] == 2) | (vlh["vlh12a_c"] == 3)
    ][["folio", "vlh13a"]]
    households_without_nna_times = pd.merge(households_without_nna, vlh_without_nna, on="folio", how="left")
    households_without_nna_times["vlh13a"] = households_without_nna_times["vlh13a"].fillna(0)
    mean_without_nna = households_without_nna_times["vlh13a"].mean()
    
    # Select households with assets where total times since 2005 > average for households without non-ag business
    result_folios = households_with_assets_times[
        households_with_assets_times["vlh13a"] > avg_times
    ][["folio"]]
    
    # Return result with Household ID
    return result_folios.reset_index(drop=True)