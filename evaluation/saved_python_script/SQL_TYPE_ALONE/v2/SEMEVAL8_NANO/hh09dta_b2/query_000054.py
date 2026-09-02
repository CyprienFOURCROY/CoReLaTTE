def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    ah = tables["ii_ah"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    
    # Filter for Oaxaca (ent == 20)
    oaxaca_portad = portad[portad["ent"] == 20]
    # Merge portad with se on 'folio'
    portad_se = pd.merge(oaxaca_portad, se, on="folio", how="inner")
    # Filter households with disease/accident/hospitalization event in last 5 years (se01b == 1)
    households_with_event = portad_se[portad_se["se01b"] == 1]
    # Filter for adults (edad >= 18)
    adults_in_households = households_with_event[households_with_event["edad"] >= 18]
    # Get unique household IDs
    household_ids = adults_in_households["folio"].unique()
    
    # Filter ah for these households
    ah_filtered = ah[ah["folio"].isin(household_ids)]
    # Filter households with at least one member owning electronic device (ah03e == 1)
    households_with_electronic = ah_filtered[ah_filtered["ah03e"] == 1]
    households_with_electronic_ids = households_with_electronic["folio"].unique()
    
    # Filter nna for these households
    nna_filtered = nna[nna["folio"].isin(household_ids)]
    # Filter households with at least one member owning/sharing non-agricultural business (nna01 == 1)
    households_with_business = nna_filtered[nna_filtered["nna01"] == 1]
    households_with_business_ids = households_with_business["folio"].unique()
    
    # Find intersection of households satisfying all three conditions
    target_households = set(household_ids) & set(households_with_electronic_ids) & set(households_with_business_ids)
    target_households = list(target_households)
    
    # Filter crh for these households
    crh_filtered = crh[crh["folio"].isin(target_households)]
    # Filter for households with total debts + interests (crh04_1 == 1)
    indebted_households = crh_filtered[crh_filtered["crh04_1"] == 1]
    # Calculate average total debts among indebted households
    avg_debt = indebted_households["crh04_2"].mean()
    
    # Filter for households with total debt exceeding the average
    households_exceeding_debt = indebted_households[indebted_households["crh04_2"] > avg_debt]
    # Count adults (edad >= 18) in these households
    adults_in_exceeding = portad[
        (portad["folio"].isin(households_exceeding_debt["folio"])) & (portad["edad"] >= 18)
    ]
    count_adults = adults_in_exceeding.shape[0]
    
    return pd.DataFrame({"adults_in_target_households": [count_adults]})