def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    
    # Calculate overall average age
    overall_avg_age = df_portad["edad"].mean()
    
    # Filter households with more adults (age >= 18) than overall average
    # First, count number of adults per household
    adults_per_folio = (
        df_portad[df_portad["edad"] >= 18]
        .groupby("folio")
        .size()
        .reset_index(name="adult_count")
    )
    
    # Merge to get each household's adult count
    households = df_portad[["folio"]]].drop_duplicates()
    households = households.merge(adults_per_folio, on="folio", how="left")
    households["adult_count"] = households["adult_count"].fillna(0)
    
    # Filter households with more adults than overall average
    households_filtered = households[households["adult_count"] > overall_avg_age]
    
    # Merge back to get members info
    df_portad_filtered = df_portad[df_portad["folio"].isin(households_filtered["folio"])]
    
    # For each household, check if any member feels unsafe or very unsafe at home
    # 'Feel safe at home' is in df_vlh: 'vlh04'
    # Values: 3 (Unsafe), 4 (Very unsafe)
    # Merge with 'ii_vlh' table
    df_vlh = tables["ii_vlh"]
    # Filter members who feel unsafe or very unsafe
    unsafe_members = df_vlh[df_vlh["vlh04"].isin([3, 4])]
    unsafe_folios = unsafe_members["folio"].unique()
    
    # Filter households with members feeling unsafe/very unsafe
    households_unsafe = households_filtered[households_filtered["folio"].isin(unsafe_folios)]
    
    # Now, filter households that have lived since 2005 or earlier
    # 'vlh02_1' indicates since what year they live in the house
    # Values: 1 (Yes), 8 (DK)
    # 'vlh02_2' is the year they live in the house
    # We consider only those with 'vlh02_1' == 1 and 'vlh02_2' <= 2005
    # First, get the relevant data
    # Merge with 'ii_vlh' to get 'vlh02_1' and 'vlh02_2'
    # Since 'vlh02_1' and 'vlh02_2' are in 'ii_vlh', merge on 'folio'
    vlh = tables["ii_vlh"]
    households_unsafe = households_unsafe.merge(
        vlh[["folio", "vlh02_1", "vlh02_2"]],
        on="folio",
        how="left"
    )
    # Filter for those who have lived since 2005 or earlier
    households_since_2005 = households_unsafe[
        (households_unsafe["vlh02_1"] == 1) & (households_unsafe["vlh02_2"] <= 2005)
    ]
    
    total_households = len(households_since_2005)
    
    # Count how many of these households produced or sold canned goods in last 12 months
    # 'ii_inr' table has 'folio' and 'inr02b' (produce/sell canned goods)
    inr = tables["ii_inr"]
    inr_filtered = inr[inr["folio"].isin(households_since_2005["folio"])]
    canned_goods_producers = inr_filtered[inr_filtered["inr02b"] == 1]
    count_canned_goods = canned_goods_producers["folio"].nunique()
    
    return pd.DataFrame({
        "total_households": [total_households],
        "households_producing_canned_goods": [count_canned_goods]
    })