def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    in_table = tables["ii_in"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Filter households that received positive amount directly from "Other Government Program" (in02a10 > 0)
    in_oaxaca = in_table[in_table["folio"].isin(oaxaca_households["folio"])]
    in_oaxaca_pos = in_oaxaca[in_oaxaca["in02a10"] > 0]
    
    # Merge to get household info
    merged = pd.merge(in_oaxaca_pos, oaxaca_households, on="folio", how="inner")
    
    # Filter households with total debts + interests > Oaxaca average
    crh_oaxaca = crh[crh["folio"].isin(merged["folio"])]
    # Replace NaN with 0 for comparison
    crh_oaxaca['crh04_2'] = crh_oaxaca['crh04_2'].fillna(0)
    average_debt = crh_oaxaca['crh04_2'].mean()
    high_debt = crh_oaxaca[crh_oaxaca['crh04_2'] > average_debt]
    
    # Merge to get household info
    result = pd.merge(high_debt, oaxaca_households, on="folio", how="inner")
    
    # Select relevant columns
    result_final = result[["folio", "crh04_2", "in02a10"]]
    # Rename columns for clarity
    result_final = result_final.rename(columns={
        "crh04_2": "total_debt_plus_interest",
        "in02a10": "received_amount"
    })
    # Sort from highest to lowest debt
    result_final = result_final.sort_values(by="total_debt_plus_interest", ascending=False).reset_index(drop=True)
    
    return result_final