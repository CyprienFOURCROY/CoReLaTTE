def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca = portad[portad["ent"] == 15]
    
    # Filter for adults aged 18+ (edad >= 18)
    adults_oaxaca = oaxaca[oaxaca["edad"] >= 18]
    
    # Merge with household data to get household info
    merged = pd.merge(adults_oaxaca, ah, on=["folio", "ls"], how="inner")
    
    # Filter for households that use a plot of land for cultivation (su01 == 1)
    households_with_plot = merged[merged["su01"] == 1]
    
    # Count adults with valid answer to "Feel safe at home?" (vlh04)
    # Valid answers are 1 (Very safe), 2 (Safe), 3 (Unsafe), 4 (Very unsafe)
    # We are interested in those who provided a valid answer (not NaN)
    valid_responses = households_with_plot[households_with_plot["vlh04"].notna()]
    total_valid = len(valid_responses)
    
    # Count how many reported feeling Unsafe or Very unsafe (vlh04 == 3 or 4)
    unsafe_responses = valid_responses[valid_responses["vlh04"].isin([3, 4])]
    count_unsafe = len(unsafe_responses)
    
    return pd.DataFrame({
        "total_adults_with_answer": [total_valid],
        "adults_feeling_unsafe": [count_unsafe]
    })