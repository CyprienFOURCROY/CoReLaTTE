def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    ah = tables["ii_ah"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20][["folio"]]
    
    # Filter households outside Oaxaca
    non_oaxaca_households = portad[portad["ent"] != 20][["folio"]]
    
    # Find households with at least one member owning a motor vehicle (ah03d == 1)
    ah_motor_vehicle = ah[ah["ah03d"] == 1][["folio"]]
    households_with_vehicle = ah_motor_vehicle.drop_duplicates(subset=["folio"])
    
    # Merge to get households in Oaxaca with at least one member owning a vehicle
    oaxaca_with_vehicle = pd.merge(oaxaca_households, households_with_vehicle, on="folio", how="inner")
    
    # Merge to get households outside Oaxaca with at least one member owning a vehicle
    non_oaxaca_with_vehicle = pd.merge(non_oaxaca_households, households_with_vehicle, on="folio", how="inner")
    
    # Filter vlh data for these households
    oaxaca_vlh = pd.merge(oaxaca_with_vehicle, vlh, on="folio", how="inner")
    non_oaxaca_vlh = pd.merge(non_oaxaca_with_vehicle, vlh, on="folio", how="inner")
    
    # Compute average 'vlh04' (feel safe at home) for households outside Oaxaca with at least one vehicle owner
    avg_vlh04_non_oaxaca = non_oaxaca_vlh["vlh04"].mean()
    
    # Filter Oaxaca households where 'vlh04' > average outside Oaxaca
    oaxaca_houses_higher_risk = oaxaca_vlh[oaxaca_vlh["vlh04"] > avg_vlh04_non_oaxaca]
    
    # Select relevant columns and sort from most unsafe (highest vlh04) to least
    result = oaxaca_houses_higher_risk[["folio", "vlh04"]].sort_values(by="vlh04", ascending=False).reset_index(drop=True)
    
    return result