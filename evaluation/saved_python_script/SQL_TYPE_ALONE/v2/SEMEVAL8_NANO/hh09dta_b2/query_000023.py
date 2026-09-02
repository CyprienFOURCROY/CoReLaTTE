def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20]
    
    # Merge households with inr to get household-level data
    merged_inr = pd.merge(oaxaca_households, df_inr, on="folio", how="inner")
    
    # Filter households that produced or sold meat in last 12 months (inr02c == 1)
    households_with_meat = merged_inr[merged_inr["inr02c"] == 1]
    
    # Compute mean age for these households
    mean_age = households_with_meat["edad"].mean()
    
    # Filter individuals in these households with age >= mean_age
    individuals_in_households = pd.merge(oaxaca_households, df_portad[["folio", "edad"]], on="folio", how="inner")
    individuals_in_households = pd.merge(individuals_in_households, df_inr[["folio", "inr02a10"]], on="folio", how="left")
    
    # Keep only individuals in households with meat production/sale
    individuals_in_households = individuals_in_households[individuals_in_households["folio"].isin(households_with_meat["folio"])]
    
    # Filter individuals with age >= mean_age
    filtered_individuals = individuals_in_households[individuals_in_households["edad"] >= mean_age]
    
    # Merge with in02a10 to get amount received from 'Other Government Program'
    # in02a10 is in df_inr, merge on 'folio'
    inr_details = df_inr[["folio", "in02a10"]]
    individuals_with_inr = pd.merge(filtered_individuals, inr_details, on="folio", how="left")
    
    # Filter individuals whose household received above-average amount from in02a10
    # First, compute household average in02a10
    household_inr_mean = df_inr.groupby("folio")["in02a10"].mean()
    # Merge household mean back to individuals
    individuals_with_inr = pd.merge(individuals_with_inr, household_inr_mean, on="folio", suffixes=("", "_household"))
    # Keep only individuals where in02a10 > household mean
    above_avg_in02a10 = individuals_with_inr[individuals_with_inr["in02a10"] > individuals_with_inr["in02a10_household"]]
    
    # For each household, get the top 10 oldest individuals
    top_individuals = (
        above_avg_in02a10
        .sort_values(["folio", "edad"], ascending=[True, False])
        .groupby("folio")
        .head(10)
    )
    
    # Select required columns
    result = top_individuals[["folio", "ls", "edad", "in02a10"]]
    
    # Rename columns for clarity
    result = result.rename(columns={"folio": "household_id", "ls": "individual_id", "edad": "age", "in02a10": "amount_received"})
    
    return result.reset_index(drop=True)