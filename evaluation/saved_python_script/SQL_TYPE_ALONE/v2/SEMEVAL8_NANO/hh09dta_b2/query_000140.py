def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    ah = tables["ii_ah"]
    in_data = tables["ii_in"]
    
    # Filter households that use land for farming (su01 == 1)
    su_land = su[su["su01"] == 1][["folio"]]
    
    # Filter households that own a motor vehicle (ah03d == 1)
    ah_vehicle = ah[ah["ah03d"] == 1][["folio"]]
    
    # Filter households with at least one member aged 60 or older (edad >= 60)
    portad_older = portad[portad["edad"] >= 60][["folio"]]
    
    # Merge filters to get households satisfying all three conditions
    filtered_folios = (
        portad_older
        .merge(su_land, on="folio", how="inner")
        .merge(ah_vehicle, on="folio", how="inner")
    )
    
    # Filter in_data for these households
    in_filtered = in_data[in_data["folio"].isin(filtered_folios["folio"])]
    
    # Select households with non-missing values for 'in02a10' (amount received directly from Other Government Program)
    in_filtered = in_filtered[~in_filtered["in02a10"].isna()]
    
    # Merge with household info to get 'ent' (state)
    household_info = portad[portad["folio"].isin(in_filtered["folio"])]
    merged = in_filtered.merge(household_info[["folio", "ent"]], on="folio", how="left")
    
    # Group by state ('ent') and compute mean of 'in02a10'
    result = (
        merged
        .groupby("ent")["in02a10"]
        .mean()
        .reset_index()
        .rename(columns={"in02a10": "avg_amount"})
    )
    
    # Rank from lowest to highest
    result = result.sort_values(by="avg_amount", ascending=True).reset_index(drop=True)
    
    return result