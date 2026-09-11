def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    vlh = tables["ii_vlh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Identify households with at least one member aged 60 or older
    age_60_plus = oaxaca_households[oaxaca_households["edad"] >= 60]
    households_with_60_plus = age_60_plus["folio"].unique()
    
    # Identify households with at least one member under 30
    under_30 = oaxaca_households[oaxaca_households["edad"] < 30]
    households_with_under_30 = under_30["folio"].unique()
    
    # Find households that satisfy both conditions
    households_both = set(households_with_60_plus).intersection(set(households_with_under_30))
    
    # Filter households in both sets
    households_both_df = oaxaca_households[oaxaca_households["folio"].isin(households_both)]
    
    # For these households, determine if any member owns/shares a non-ag business
    nna_filtered = nna[nna["folio"].isin(households_both)]
    # Create a mapping from folio to ownership status
    ownership_map = nna_filtered.groupby("folio")["nna01"].max()
    # Map ownership status to households
    ownership_status = ownership_map.reindex(households_both).fillna(2)  # default to 'No' if missing
    
    # Prepare a DataFrame with folio and ownership status
    households_df = pd.DataFrame({
        "folio": list(households_both),
        "owns_non_ag": ownership_status.values
    })
    
    # For each household, check if any member owns/shares non-ag business
    # Since ownership info is at household level, we can directly use ownership_status
    
    # Count households grouped by ownership status
    result = households_df.groupby("owns_non_ag").size().reset_index(name="household_count")
    # Map ownership status codes to labels
    ownership_labels = {1: "Yes", 2: "No"}
    result["owns_non_ag"] = result["owns_non_ag"].map(ownership_labels)
    
    return result