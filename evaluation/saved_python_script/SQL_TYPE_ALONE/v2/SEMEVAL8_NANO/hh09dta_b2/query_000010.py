def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    se = tables["ii_se"]
    
    # Merge ah and se on folio and ls
    merged = pd.merge(ah, se, on=["folio", "ls"], how="inner")
    
    # Filter households that experienced a disease, accident, or hospitalization in last 5 years
    condition = (
        (merged["se01b"] == 1) |  # disease/accident/hospital
        (merged["se01c"] == 1) |  # unemployment/failure
        (merged["se01d"] == 1) |  # natural disaster
        (merged["se01e"] == 1) |  # lost crop
        (merged["se01f"] == 1)    # lost/robbery/dead animal
    )
    households_with_event = merged[condition]
    
    # Keep only relevant columns
    relevant = households_with_event[["folio", "se02fa_1", "se02fa_2"]]
    
    # Merge with portad to get 'ent' (state)
    full_data = pd.merge(relevant, portad[["folio", "ent"]], on="folio", how="left")
    
    # Filter households that reported having electronic devices (se02fa_1 == 1)
    electronic_devices = full_data[full_data["se02fa_1"] == 1]
    
    # Group by state ('ent') and compute:
    # - count of households with at least one reported case (se02fa_1 == 1)
    # - sum of reported number of electronic devices (se02fa_2)
    group = electronic_devices.groupby("ent").agg(
        households_count=pd.NamedAgg(column="folio", aggfunc="count"),
        total_devices=pd.NamedAgg(column="se02fa_2", aggfunc="sum")
    ).reset_index()
    
    # Filter states with at least 2 households
    filtered = group[group["households_count"] >= 2]
    
    # Calculate average number of electronic devices per household for each state
    filtered["avg_devices"] = filtered["total_devices"] / filtered["households_count"]
    
    # Select top 10 states with highest average reported value
    top10 = (
        filtered.sort_values(by="avg_devices", ascending=False)
        .head(10)
        [["ent", "households_count", "avg_devices"]]
    )
    
    # Map 'ent' codes to state names (optional, not required for output)
    # But since only codes are present, output as is.
    
    # Rename columns for clarity
    top10 = top10.rename(columns={
        "ent": "state_code",
        "households_count": "households",
        "avg_devices": "average_reported_devices"
    })
    
    return top10.reset_index(drop=True)