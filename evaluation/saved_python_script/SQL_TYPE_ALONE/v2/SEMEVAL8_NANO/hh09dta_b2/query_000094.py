def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_vlh = tables["ii_vlh"]
    
    # Filter for Oaxaca (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20]
    
    # Calculate average age in Oaxaca
    avg_age = oaxaca_portad["edad"].mean()
    
    # Merge portad with se on 'folio'
    merged = pd.merge(oaxaca_portad, df_se, on="folio", how="inner")
    
    # Filter for individuals older than average age
    older_individuals = merged[merged["edad"] > avg_age]
    
    # Filter for individuals in households that reported knowing a family or friend robbed in last 12 months
    # and reported no household member death in last five years
    # Conditions:
    # - 'vlh10a' == 1 (knows family/friend robbed house in last 12 months)
    # - 'se01a' == 3 (no household member death in last five years)
    # Merge with vlh on 'folio' to get 'vlh10a' and 'vlh10b' etc.
    merged_vlh = pd.merge(older_individuals, df_vlh, on="folio", how="left")
    
    # Apply conditions
    condition = (
        (merged_vlh["vlh10a"] == 1) &
        (merged_vlh["se01a"] == 3)
    )
    
    result_df = merged_vlh[condition]
    
    # Count the number of individuals satisfying all conditions
    count = len(result_df)
    
    return pd.DataFrame({"count": [count]})