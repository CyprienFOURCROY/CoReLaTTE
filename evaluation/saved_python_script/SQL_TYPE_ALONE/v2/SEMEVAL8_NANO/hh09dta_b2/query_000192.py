def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    inr = tables["ii_inr"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Merge with se to get egg production info
    merged_se = pd.merge(oaxaca_households, se, on="folio", how="inner")
    
    # Filter households that produce/sell eggs in last 12 months (inr02d == 1)
    # First, merge with inr to get egg production info
    merged_inr = pd.merge(merged_se, inr, on="folio", how="inner")
    egg_producers = merged_inr[merged_inr["inr02d"] == 1]
    
    # Filter households that use a plot of land for farming (su01 == 1)
    # Merge with inr_enriched to get su01 info
    inr_enriched = tables["ii_inr_enriched"]
    egg_producers = pd.merge(egg_producers, inr_enriched[["folio", "su01"]], on="folio", how="inner")
    land_farmers = egg_producers[egg_producers["su01"] == 1]
    
    # Filter households that reported producing/selling eggs last month (inr04d == 1)
    last_month_eggs = land_farmers[land_farmers["inr04d"] == 1]
    
    # Get total eggs sold last month (inr03d)
    eggs_sold = last_month_eggs[["folio", "inr03d"]]
    
    # Calculate the national average number of eggs sold last month
    avg_eggs = eggs_sold["inr03d"].mean()
    
    # Select households that sold at least the average
    households_above_avg = eggs_sold[eggs_sold["inr03d"] >= avg_eggs]
    
    # Prepare the result DataFrame
    result = households_above_avg[["folio", "inr03d"]].rename(columns={"folio": "household_id", "inr03d": "eggs_sold_last_month"})
    
    return result.reset_index(drop=True)