def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]
    
    # Filter Oaxaca households (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20]
    
    # Merge with nna to get non-ag business info
    merged_nna = pd.merge(
        oaxaca_portad,
        df_nna,
        on="folio",
        how="left"
    )
    
    # Filter households that own/share non-ag business (nna01 == 1)
    nna_own = merged_nna[merged_nna["nna01"] == 1]
    
    # Filter households without non-ag business (nna01 == 2)
    nna_no = merged_nna[merged_nna["nna01"] == 2]
    
    # Merge with ii_ah to get domestic appliances info
    ah_merged = pd.merge(
        nna_own,
        df_ah,
        on=["folio", "ls"],
        how="left"
    )
    ah_no = pd.merge(
        nna_no,
        df_ah,
        on=["folio", "ls"],
        how="left"
    )
    
    # Filter for highest-valued domestic appliance > 8 (more than DK)
    ah_own_filtered = ah_merged[ah_merged["ah04m_2"] > 8]
    ah_no_filtered = ah_no[ah_no["ah04m_2"] > 8]
    
    # Calculate average highest-valued domestic appliance among households without non-ag business
    avg_value_no = ah_no_filtered["ah04m_2"].mean()
    
    # Select households that own/share non-ag business with highest-valued domestic appliance > average
    result = ah_own_filtered[ah_own_filtered["ah04m_2"] > avg_value_no]
    
    # Select relevant columns and sort from highest to lowest
    result_sorted = result[["folio", "ls", "ah04m_2"]].sort_values(by="ah04m_2", ascending=False)
    
    return result_sorted.reset_index(drop=True)