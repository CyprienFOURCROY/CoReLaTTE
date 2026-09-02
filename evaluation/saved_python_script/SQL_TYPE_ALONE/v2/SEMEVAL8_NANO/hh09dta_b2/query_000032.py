def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    vlh = tables["ii_vlh"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge crh with portad on 'folio'
    crh_oaxaca = crh.merge(oaxaca_households[["folio"]], on="folio", how="inner")
    
    # Filter households that feel unsafe or very unsafe at home (vlh04 == 3 or 4)
    vlh_filtered = vlh[vlh["vlh04"].isin([3, 4])]
    
    # Merge vlh with portad to get household info
    vlh_oaxaca = vlh_filtered.merge(oaxaca_households[["folio"]], on="folio", how="inner")
    
    # Merge vlh with crh to get debts info
    vlh_crh = vlh_oaxaca.merge(crh_oaxaca[["folio", "crh04_2"]], on="folio", how="left")
    
    # Drop rows where crh04_2 (total debts + interests) is NaN
    vlh_crh_clean = vlh_crh.dropna(subset=["crh04_2"])
    
    # Calculate the average total debts + interests among households feeling unsafe
    avg_debt = vlh_crh_clean["crh04_2"].mean()
    
    # Filter households with total debts > average
    households_above_avg = vlh_crh_clean[vlh_crh_clean["crh04_2"] > avg_debt]
    
    # Select household ID and amount, order from highest to lowest
    result = households_above_avg[["folio", "crh04_2"]].sort_values(by="crh04_2", ascending=False)
    
    # Rename columns for clarity
    result = result.rename(columns={"folio": "Household ID", "crh04_2": "Total Debts + Interests (Pesos)"})
    
    return result.reset_index(drop=True)