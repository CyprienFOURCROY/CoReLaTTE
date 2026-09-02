def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_nna = tables["ii_nna"]
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]
    df_nna_enriched = tables["ii_nna_enriched"]
    df_su_enriched = tables["ii_su_enriched"]
    df_ah_enriched = tables["ii_ah_enriched"]
    
    # Filter households where at least one member owns/shares a non-agricultural business
    nna_owners = df_nna_enriched[df_nna_enriched["nna01"] == 1][["folio"]]
    
    # Filter households that use a plot/land for farming
    land_use = df_su_enriched[df_su_enriched["su01"] == 1][["folio"]]
    
    # Merge to get households satisfying both conditions
    households = pd.merge(nna_owners, land_use, on="folio", how="inner")
    
    # Get relevant household IDs
    household_ids = households["folio"].unique()
    
    # Filter df_in for these households
    df_in_filtered = df_in[df_in["folio"].isin(household_ids)]
    
    # Filter for households with positive direct payment from "Other Government Program" (in02a10)
    # and amount > 0
    df_in_filtered = df_in_filtered[
        (df_in_filtered["in02a10"] > 0) & (~df_in_filtered["in02a10"].isna())
    ]
    
    # Calculate the mean of in02a10 for households satisfying the conditions
    mean_in02a10 = df_in_filtered["in02a10"].mean()
    
    # Select households with in02a10 > mean
    result = df_in_filtered[df_in_filtered["in02a10"] > mean_in02a10]
    
    # Prepare output: household ID and amount received, sorted descending
    output = result[["folio", "in02a10"]].dropna(subset=["in02a10"])
    output = output.sort_values(by="in02a10", ascending=False).reset_index(drop=True)
    
    return output