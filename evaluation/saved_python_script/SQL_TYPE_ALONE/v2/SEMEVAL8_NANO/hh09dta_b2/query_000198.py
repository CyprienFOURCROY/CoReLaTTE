def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    ah = tables["ii_ah"]
    
    # Filter households in Oaxaca (ent == 15)
    oaxaca_households = portad[portad["ent"] == 15]
    
    # Merge with household ownership info
    ah_filtered = ah[ah["folio"].isin(oaxaca_households["folio"])]
    
    # Filter households with at least one member owning an electronic device (ah03e == 1)
    households_with_electronic = ah_filtered[ah_filtered["ah03e"] == 1]
    
    # Get the set of household IDs with electronic devices
    households_with_electronic_ids = set(households_with_electronic["folio"])
    
    # Filter households in Oaxaca with at least one member owning an electronic device
    oaxaca_with_electronic = oaxaca_households[
        oaxaca_households["folio"].isin(households_with_electronic_ids)
    ]
    
    # Merge with nna to get ownership/sharing info
    nna_filtered = nna[nna["folio"].isin(oaxaca_with_electronic["folio"])]
    
    # For each household, determine if any member owns/shares a non-ag business (nna01 == 1)
    nna_grouped = nna_filtered.groupby("folio")["nna01"].any().reset_index()
    nna_grouped["nna01"] = nna_grouped["nna01"].astype(bool)
    
    # Merge back with household list
    result_df = oaxaca_with_electronic.merge(nna_grouped, on="folio", how="left")
    
    # Count households with non-ag business ownership/sharing
    count_with_business = result_df["nna01"].sum()
    total_households = len(result_df)
    count_without_business = total_households - count_with_business
    
    return pd.DataFrame(
        {
            "households_with_non_ag_business": [count_with_business],
            "households_without_non_ag_business": [count_without_business]
        }
    )