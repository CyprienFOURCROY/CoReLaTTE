def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    
    # Filter individuals living in households that report feeling unsafe or very unsafe at home
    # 'vlh04' indicates feeling safe at home:
    # 1: Very safe, 2: Safe, 3: Unsafe, 4: Very unsafe
    unsafe_mask = portad["vlh04"].isin([3, 4])
    unsafe_portad = portad[unsafe_mask]
    
    # Merge with 'se' on 'folio' to get the survey responses
    merged = pd.merge(unsafe_portad, se, on="folio", how="inner")
    
    # Filter individuals where 'vlh04' indicates unsafe or very unsafe
    # Already done via 'unsafe_mask'
    
    # Group by 'ent' (state) and compute the count and mean age
    group = merged.groupby("ent").agg(
        count=("edad", "size"),
        average_age=("edad", "mean")
    ).reset_index()
    
    # Filter states with at least 10 such individuals
    filtered = group[group["count"] >= 10]
    
    # Rank from highest to lowest average age
    ranked = filtered.sort_values(by="average_age", ascending=False)
    
    # Select only 'ent' and 'average_age' columns for output
    result = ranked[["ent", "average_age"]]
    
    return result