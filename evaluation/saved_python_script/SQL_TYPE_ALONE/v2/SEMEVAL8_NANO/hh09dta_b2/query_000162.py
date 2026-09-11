def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    
    # Filter for Oaxaca (ent=20)
    portad_oaxaca = portad[portad["ent"] == 20]
    
    # Merge portad with nna on 'folio'
    merged = pd.merge(portad_oaxaca, nna, on="folio", how="left")
    
    # Identify households that own or share a non-agricultural business (nna01 == 1)
    households_with_business = merged[merged["nna01"] == 1]["folio"].unique()
    
    # Separate households without such a business
    households_without_business = merged[~merged["folio"].isin(households_with_business)]
    
    # Compute average age in households without such a business
    avg_age = households_without_business["edad"].mean()
    
    # Filter individuals in households with business
    individuals_in_business_households = merged[merged["folio"].isin(households_with_business)]
    
    # Select individuals with age >= average age
    result = individuals_in_business_households[individuals_in_business_households["edad"] >= avg_age]
    
    # Select relevant columns
    result = result[["folio", "ls", "edad"]]
    
    # Rename columns if needed (not necessary)
    return result