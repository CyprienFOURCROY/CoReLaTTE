def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    ah = tables["ii_ah"]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca = portad[portad["ent"] == 15]
    
    # Merge with household info from 'ah' to get poultry ownership
    ah_subset = ah[["folio", "ah03m"]]
    household_info = oaxaca.merge(ah_subset, on="folio", how="inner")
    
    # Filter for households with forced-entry robbery since 2005 (vlh12a_c == 1)
    # First, get households with such robberies
    vlh = tables["ii_vlh"]
    rob_households = vlh[
        (vlh["vlh12a_c"] == 1)
    ][["folio"]].drop_duplicates()
    
    # Filter households that experienced such robberies
    households_with_robbery = household_info[
        household_info["folio"].isin(rob_households["folio"])
    ]
    
    # Merge with 'ah' to get adult individuals info
    ah_full = ah[["folio", "ls", "ah03a"]]
    individuals = households_with_robbery.merge(ah_full, on="folio", how="inner")
    
    # Filter for adults (18+)
    adults = individuals[individuals["ah03a"] >= 18]
    
    # Merge with portad to get age info
    adults = adults.merge(portad[["folio", "edad"]], on="folio", how="left")
    
    # Filter for adults in households that experienced the robbery
    # Already filtered by 'households_with_robbery'
    
    # Calculate overall mean age
    mean_age = adults["edad"].mean()
    
    # Determine if each adult is older than the overall mean
    adults["older_than_mean"] = adults["edad"] > mean_age
    
    # Determine poultry ownership at household level
    # For each household, check if any member owns poultry (ah03m == 1)
    household_poultry = ah.groupby("folio")["ah03m"].apply(lambda x: (x == 1).any()).reset_index()
    household_poultry.rename(columns={"ah03m": "has_poultry"}, inplace=True)
    
    # Merge with adults
    adults = adults.merge(household_poultry, on="folio", how="left")
    
    # Group by poultry ownership
    result = (
        adults.groupby("has_poultry")
        .agg(
            average_age=("edad", "mean"),
            count_older=("older_than_mean", "sum")
        )
        .reset_index()
    )
    
    # Map boolean to descriptive
    result["has_poultry"] = result["has_poultry"].map({True: "Owns Poultry", False: "Does Not Own Poultry"})
    
    return result[['has_poultry', 'average_age', 'count_older']]