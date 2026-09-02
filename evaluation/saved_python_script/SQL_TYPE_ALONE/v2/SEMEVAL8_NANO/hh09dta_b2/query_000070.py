def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_se = tables["ii_se"]
    
    # Merge household data with ii_ah on 'folio' and 'ls'
    merged = pd.merge(df_portad, df_ah, on=["folio", "ls"], how="inner")
    # Merge the result with ii_se on 'folio'
    merged = pd.merge(merged, df_se[["folio", "se01a"]], on="folio", how="left")
    
    # Filter households with positive monetary value for electronic devices
    # Values are in 'ah04e_2' (value of electronic device)
    filtered = merged[merged["ah04e_2"] > 0]
    
    # Calculate the average number of household members ('edad' column)
    avg_members = filtered["edad"].mean()
    
    return pd.DataFrame(
        {"average_household_members": [avg_members]}
    )