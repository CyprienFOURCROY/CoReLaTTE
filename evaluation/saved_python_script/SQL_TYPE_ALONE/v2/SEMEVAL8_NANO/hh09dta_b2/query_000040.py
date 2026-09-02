def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20]
    
    # Merge with ii_vlh on 'folio' to get 'vlh03' (Feel safe at home?) info
    merged = pd.merge(oaxaca_households, df_vlh, on="folio", how="inner")
    
    # Filter for households with valid 'vlh04' (Feel safe at home?) responses
    valid_responses = merged[merged["vlh04"].notna()]
    
    # Group by 'vlh04' and compute the number of adults (edad >= 18) per household
    # First, identify adults in each household
    # For each household, count number of individuals with edad >= 18
    adults = valid_responses[valid_responses["edad"] >= 18]
    adults_count = adults.groupby("folio").size().reset_index(name="adult_count")
    
    # Merge back to get household responses
    household_responses = valid_responses[["folio", "vlh04"]].drop_duplicates()
    combined = pd.merge(household_responses, adults_count, on="folio", how="left")
    
    # For households with no adults, fill 0
    combined["adult_count"] = combined["adult_count"].fillna(0)
    
    # Map 'vlh04' responses to categories
    response_map = {
        1: "Very safe",
        2: "Safe",
        3: "Unsafe",
        4: "Very unsafe"
    }
    combined["response_category"] = combined["vlh04"].map(response_map)
    
    # Compute average number of adults per household for each response category
    result = combined.groupby("response_category")["adult_count"].mean().reset_index()
    
    # Rename columns for clarity
    result.columns = ["Response", "Average_Adults"]
    
    return result