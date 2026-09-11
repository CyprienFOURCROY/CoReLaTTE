def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_in = tables["ii_inr"]
    df_robberies = tables["ii_vlh"]
    
    # Filter households with any debt in last 12 months
    debt_mask = df_in["crh02_1"] == 1
    households_with_debt = df_in[debt_mask][["folio", "crh02b"]].dropna()

    # Calculate average number of robberies since 2005 among households with any such robberies
    # First, filter households that have entered/robbed since 2005
    robbery_mask = (
        (df_robberies["vlh12a_a"] == 1) | 
        (df_robberies["vlh12a_b"] == 1)
    )
    df_robbery_since_2005 = df_robberies[robbery_mask]
    
    # Group by household and sum total robberies since 2005
    robbery_counts = df_robbery_since_2005.groupby("folio")["vlh13a"].sum().reset_index()
    # Filter households with at least one robbery since 2005
    households_with_robbery = robbery_counts[robbery_counts["vlh13a"] > 0]
    
    # Compute mean number of robberies since 2005
    mean_robberies = households_with_robbery["vlh13a"].mean()
    
    # Select households with total robberies since 2005 greater than the mean
    high_robbery_households = households_with_robbery[
        households_with_robbery["vlh13a"] > mean_robberies
    ]
    
    # Merge to get household IDs with their robbery counts
    merged = pd.merge(
        households_with_debt,
        high_robbery_households,
        on="folio",
        how="inner"
    )
    
    # Merge with debt amount
    result = pd.merge(
        merged,
        df_in[["folio", "crh02b"]],
        on="folio",
        how="left"
    )
    
    # Filter for households that reported a pesos amount owed (crh02b > 0)
    # Note: crh02b indicates amount in pesos owed; check for non-null and > 0
    result_filtered = result[
        (result["crh02b"].notnull()) & (result["crh02b"] > 0)
    ][["folio", "vlh13a", "crh02b"]]
    
    # Rename columns for clarity
    result_filtered = result_filtered.rename(
        columns={
            "folio": "Household_ID",
            "vlh13a": "Incident_Count_Since_2005",
            "crh02b": "Owed_Pesos_Amount"
        }
    )
    
    return result_filtered.reset_index(drop=True)