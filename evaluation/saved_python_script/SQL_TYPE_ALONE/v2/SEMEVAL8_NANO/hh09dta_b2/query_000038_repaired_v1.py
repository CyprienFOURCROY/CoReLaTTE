def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    vlh = tables["ii_vlh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge household info with household ID (folio)
    households = oaxaca_households[["folio"]]
    
    # Filter households where feeling unsafe or very unsafe at home
    # "vlh04" indicates feeling safe at home:
    # 1: Very safe, 2: Safe, 3: Unsafe, 4: Very unsafe
    unsafe_mask = (vlh["vlh04"] == 3) | (vlh["vlh04"] == 4)
    households_vlh = vlh[unsafe_mask]
    
    # Merge with households to keep only those in Oaxaca and feeling unsafe
    households_in_oaxaca = households.merge(households_vlh[["folio"]], on="folio", how="inner")
    
    # For each household, check if at least one adult (edad >= 18)
    # Merge with portad to get ages
    household_ages = portad[portad["folio"].isin(households_in_oaxaca["folio"])]
    has_adult = household_ages.groupby("folio")["edad"].apply(lambda x: (x >= 18).any())
    
    # Merge with ah to check for ownership of motor vehicle
    household_ah = ah[ah["folio"].isin(households_in_oaxaca["folio"])]
    owns_motor_vehicle = household_ah.groupby("folio")["ah03d"].apply(lambda x: (x == 1).any())
    
    # Combine the two conditions
    household_flags = pd.DataFrame({
        "has_adult": has_adult,
        "owns_motor_vehicle": owns_motor_vehicle
    })
    
    # Filter households that have at least one adult and at least one owner of motor vehicle
    qualifying_households = household_flags[
        (household_flags["has_adult"]) & (household_flags["owns_motor_vehicle"])
    ]
    
    # Count the number of such households
    count = len(qualifying_households)
    
    return pd.DataFrame({"count": [count]})