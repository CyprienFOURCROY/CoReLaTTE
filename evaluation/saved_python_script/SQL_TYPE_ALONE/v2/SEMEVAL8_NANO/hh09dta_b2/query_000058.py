def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    crh = tables["ii_crh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge with se to identify households with disease/accident/hospitalization event in last 5 years
    se_merged = pd.merge(oaxaca_households, se, on="folio", how="inner")
    
    # Filter households that reported any event in last 5 years (se01b, se01c, se01d, se01e, se01f)
    # According to the schema, these columns indicate events; presence of '1' indicates occurrence
    event_mask = (
        (se_merged["se01b"] == 1) |
        (se_merged["se01c"] == 1) |
        (se_merged["se01d"] == 1) |
        (se_merged["se01e"] == 1) |
        (se_merged["se01f"] == 1)
    )
    households_with_event = se_merged[event_mask]
    
    # Merge with crh to get total debts + interests (crh04_2)
    crh_relevant = crh[crh["folio"].isin(households_with_event["folio"])]
    
    # Drop rows with NaN in crh04_2
    crh_valid = crh_relevant.dropna(subset=["crh04_2"])
    
    # Calculate the average of total debts + interests
    avg_debt = crh_valid["crh04_2"].mean()
    
    # Filter households with total debts + interests above the average
    above_avg = crh_valid[crh_valid["crh04_2"] > avg_debt]
    
    # Count unique households in Oaxaca with such debts
    count_households = above_avg["folio"].nunique()
    
    # Return as DataFrame
    return pd.DataFrame({"households_above_avg_debt": [count_households]})