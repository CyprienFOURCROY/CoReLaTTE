def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_in = tables["ii_in"]
    df_nna = tables["ii_nna"]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca_portad = df_portad[df_portad["ent"] == 15]
    
    # Filter for age >= 60
    seniors = oaxaca_portad[oaxaca_portad["edad"] >= 60]
    
    # Get household IDs of seniors
    household_ids = seniors["folio"].unique()
    
    # Filter households that both use land for farming and own/share non-ag business
    # Land use for farming: su01 == 1
    land_use = df_su[(df_su["folio"].isin(household_ids)) & (df_su["su01"] == 1)]
    households_with_land = land_use["folio"].unique()
    
    # Households that own/share non-ag business: nna01 == 1
    nna_info = df_nna[(df_nna["folio"].isin(household_ids)) & (df_nna["nna01"] == 1)]
    households_with_nna = nna_info["folio"].unique()
    
    # Households that meet both conditions
    eligible_households = set(households_with_land).intersection(set(households_with_nna))
    
    # Filter households that reported receiving income from the Other Government Program in last 12 months
    in_eligible = df_in[(df_in["folio"].isin(eligible_households)) & (df_in["in01a10_1"] == 1)]
    
    # Calculate total direct receipts from the program
    in_eligible = in_eligible.copy()
    in_eligible["amount"] = in_eligible["in02a10"]
    
    # Group by household and compute average amount
    household_avg = in_eligible.groupby("folio")["amount"].mean().reset_index()
    
    # Compute overall average
    overall_avg = household_avg["amount"].mean()
    
    # Filter households with per-household average above overall average
    above_avg = household_avg[household_avg["amount"] > overall_avg]
    
    # Merge with household info to get household IDs
    result = above_avg[["folio", "amount"]].sort_values(by="amount", ascending=False).reset_index(drop=True)
    
    # Return as DataFrame
    return result