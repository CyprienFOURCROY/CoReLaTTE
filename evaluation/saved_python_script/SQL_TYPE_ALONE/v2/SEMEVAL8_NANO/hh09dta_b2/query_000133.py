def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge with crh to get household info and filter for households with total debts + interests reported
    crh_merged = pd.merge(oaxaca_households, crh, on="folio", how="inner")
    
    # Filter for members aged 18 or older
    members_18_plus = crh_merged[crh_merged["edad"] >= 18]
    
    # Filter for households with non-missing total debts + interests (crh04_2)
    members_with_debt = members_18_plus[members_18_plus["crh04_2"].notna()]
    
    # Group by household (folio) to compute total debts + interests
    household_debts = members_with_debt.groupby("folio")["crh04_2"].mean().reset_index()
    household_debts.rename(columns={"crh04_2": "avg_debt"}, inplace=True)
    
    # Calculate overall average debt
    overall_avg_debt = household_debts["avg_debt"].mean()
    
    # Merge to get land use info
    household_land_use = pd.merge(oaxaca_households[["folio", "ls"]], household_debts, on="folio", how="inner")
    
    # Group by land use: Yes (ls == '02') and No (ls != '02')
    land_use_groups = household_land_use.groupby("ls")["avg_debt"].mean().reset_index()
    
    # Map '02' to 'Yes' and others to 'No' for clarity
    land_use_groups["group"] = land_use_groups["ls"].apply(lambda x: "Yes" if x == "02" else "No")
    
    # Filter groups for those above the overall average debt
    above_avg = land_use_groups[land_use_groups["avg_debt"] > overall_avg_debt]
    
    # Sort from highest to lowest average debt
    result = above_avg.sort_values(by="avg_debt", ascending=False)[["group", "avg_debt"]]
    
    return result.reset_index(drop=True)