def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    inr = tables["ii_inr"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge with crh on 'folio' to get household info
    crh_merged = pd.merge(oaxaca_households, crh, on="folio", how="inner")
    
    # Filter households that reported producing or selling dairy products in last 12 months
    # inr02a == 1 indicates 'Yes' for dairy produce/sell
    dairy_households = crh_merged[crh_merged["inr02a"] == 1]
    
    # Merge with inr table to get household members' data
    household_inr = pd.merge(dairy_households, inr, on="folio", how="inner")
    
    # Filter for individual with ls == '01'
    individual_ls_01 = household_inr[household_inr["ls"] == 1]
    
    # Calculate the mean age
    avg_age = individual_ls_01["edad"].mean()
    
    return pd.DataFrame(
        {"average_age": [avg_age]}
    )