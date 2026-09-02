def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Filter households with at least one adult (edad >= 18)
    adult_households = oaxaca_households[oaxaca_households["edad"] >= 18]
    
    # Get household IDs with land use for farming (su01 == 1)
    su_farming = su[su["su01"] == 1]
    
    # Merge to get households that meet all criteria
    merged = adult_households.merge(su_farming[["folio"]], on="folio", how="inner")
    
    # Merge with crh to get debt info
    merged_crh = merged.merge(crh[["folio", "crh03_2", "crh04_2"]]], on="folio", how="inner")
    
    # Filter for numeric values in 'crh03_2' and 'crh04_2'
    debt_filtered = merged_crh[
        merged_crh["crh03_2"].notna() & merged_crh["crh04_2"].notna()
    ]
    
    # Calculate average total debt plus interest
    avg_debt = debt_filtered["crh04_2"].mean()
    
    # Filter for total debts above the group’s average
    above_avg = debt_filtered[debt_filtered["crh04_2"] > avg_debt]
    
    # Select relevant columns and sort from highest to lowest
    result = above_avg[["folio", "crh04_2"]].sort_values(by="crh04_2", ascending=False).reset_index(drop=True)
    
    return result