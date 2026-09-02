def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]
    
    # Filter portad for Oaxaca (ent == 15) and age between 30 and 60
    oaxaca_portad = df_portad[(df_portad["ent"] == 15) & (df_portad["edad"] >= 30) & (df_portad["edad"] <= 60)]
    
    # Merge portad with in to get household info
    merged_in = pd.merge(oaxaca_portad, df_in, on="folio", how="inner")
    
    # Filter households with positive amount received from "in02a10" (Other Government Program)
    # The columns "in02a10" contains the amount received directly
    households_with_ogp = merged_in[merged_in["in02a10"] > 0]
    
    # Merge with household assets to get electronic device info for individual 2
    merged_ah = pd.merge(households_with_ogp, df_ah, on=["folio", "ls"], how="inner")
    
    # Filter for individual 2 (ls == 2)
    individual2 = merged_ah[merged_ah["ls"] == 2]
    
    # Filter for electronic device value (ah04e_2) > 0
    electronic_devices = individual2[individual2["ah04e_2"] > 0]
    
    # Calculate the average electronic device value for all households in this group
    # First, get the group of households (by folio) to compute the mean
    household_group = electronic_devices.groupby("folio")["ah04e_2"].mean().reset_index(name="mean_ah04e_2")
    
    # Compute the overall average of these household means
    overall_avg = household_group["mean_ah04e_2"].mean()
    
    # Filter households whose electronic device value exceeds the group average
    top_households = household_group[household_group["mean_ah04e_2"] > overall_avg]
    
    # Merge back to get household info for top households
    result = pd.merge(top_households, households_with_ogp, on="folio", how="left")
    
    # Select top 10 households by electronic device value
    top10 = result.sort_values(by="mean_ah04e_2", ascending=False).head(10)
    
    # Return relevant columns
    return top10[["folio", "mean_ah04e_2"]]