def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    in_df = tables["ii_in"]
    ah_df = tables["ii_ah"]
    crh_df = tables["ii_crh"]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca_portad = portad[portad["ent"] == 15]
    
    # Merge portad with in_df on 'folio'
    merged = pd.merge(oaxaca_portad, in_df, on="folio", how="inner")
    
    # Filter for adult household heads (assuming 'rel' indicates household head; if not, assume 'edad' >= 18)
    # Since 'rel' is not explicitly defined as household head, use 'edad' >= 18 as proxy
    adults = merged[merged["edad"] >= 18]
    
    # Filter for households that answered "No" to "No had entered force robbery since 2005?"
    # 'vlh12a' indicates "No had entered force rob in HH since 2005?" with value 3
    # Merge with ii_vlh to get 'vlh12a' info
    # First, get households in adults
    households = adults[["folio"]].drop_duplicates()
    # Merge with ii_vlh
    # Note: 'folio' in 'tables["ii_vlh"]' is the key
    vlh = tables["ii_vlh"]
    households_vlh = pd.merge(households, vlh[["folio", "vlh12a"]], on="folio", how="left")
    # Filter for households with 'vlh12a' == 3 (no entry since 2005)
    households_no_robbery = households_vlh[households_vlh["vlh12a"] == 3]
    # Filter adults to only those in these households
    adults_no_robbery = adults[adults["folio"].isin(households_no_robbery["folio"])]
    
    # Filter for households reporting positive value for electronic devices
    # 'ah04e_2' indicates value of electronic device; positive means > 0
    ah = tables["ii_ah"]
    ah_electronics = ah[ah["ah04e_2"] > 0]
    # Merge with adults_no_robbery to filter
    adults_electronics = pd.merge(adults_no_robbery, ah_electronics[["folio"]], on="folio", how="inner")
    
    # Merge with 'ii_crh' to get 'crh01_1a' for household ownership info
    crh = tables["ii_crh"]
    adults_crh = pd.merge(adults_electronics, crh[["folio", "crh01_1a"]], on="folio", how="left")
    
    # Filter for household head ownership of living house ('crh01_1a' == 2)
    # But the question is about adult household heads, so ensure 'rel' indicates head
    # Since 'rel' is not explicitly defined, assume 'rel' indicates relation, and 'rel' == 1 indicates head
    # If 'rel' is not relation, fallback to 'edad' >= 18 and 'rel' is not null
    # But better to assume 'rel' == 1 indicates household head
    adults_heads = adults_crh[adults_crh["rel"] == 1]
    household_heads = adults_heads[adults_heads["crh01_1a"] == 2]
    
    # Now, for these household heads, get electronic device values
    # Merge with 'ah' to get 'ah04e_2' (value of electronic device)
    merged_final = pd.merge(household_heads, ah[["folio", "ah04e_2"]], on="folio", how="left")
    
    # Filter for electronic device value > 0
    electronic_heads = merged_final[merged_final["ah04e_2"] > 0]
    
    # Calculate overall average of electronic device values among this group
    overall_avg = electronic_heads["ah04e_2"].mean()
    
    # Filter for those with electronic device value above the overall average
    above_avg = electronic_heads[electronic_heads["ah04e_2"] > overall_avg]
    
    # Calculate the mean age of these individuals
    avg_age = above_avg["edad"].mean()
    
    # Prepare result DataFrame
    result = pd.DataFrame({
        "number_above_average": [len(above_avg)],
        "average_age": [avg_age]
    })
    return result