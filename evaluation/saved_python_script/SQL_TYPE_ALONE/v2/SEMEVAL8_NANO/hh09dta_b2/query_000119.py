def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    ah = tables["ii_ah"]
    inr = tables["ii_inr"]
    nna = tables["ii_nna"]
    ah_enriched = tables["ii_ah_enriched"]
    su_enriched = tables["ii_su_enriched"]
    portad_enriched = tables["ii_portad"]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca_portad = portad[portad["ent"] == 15]
    
    # Filter for members aged 18 or older
    members_18_plus = oaxaca_portad[oaxaca_portad["edad"] >= 18]
    
    # Get household IDs with at least one member aged 18 or older
    households_with_adult = members_18_plus["folio"].unique()
    
    # Filter households that have land for cultivation (su.su01 == 1)
    su_oaxaca = su[su["folio"].isin(households_with_adult)]
    households_with_land = su_oaxaca[su_oaxaca["su01"] == 1]["folio"]
    
    # Filter households where individual with ID 1 reports ownership of a motor vehicle (ah owns motor vehicle)
    ah_oaxaca = ah_enriched[ah_enriched["folio"].isin(households_with_land)]
    ah_motor_vehicle = ah_oaxaca[
        (ah_oaxaca["ls"] == 1) &  # Individual ID 1
        (ah_oaxaca["ah03d"] == 1)  # Owns motor vehicle
    ]
    
    # Final household IDs
    result_households = ah_motor_vehicle["folio"].unique()
    
    # Return as DataFrame
    return pd.DataFrame({"household_id": result_households})