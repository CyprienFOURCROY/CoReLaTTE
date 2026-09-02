def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]
    
    # Filter for Oaxaca households (ent == 15)
    oaxaca_households = df_portad[df_portad["ent"] == 15]
    
    # Filter households that use a plot/land for farming (su01 == 1)
    households_with_land = oaxaca_households.merge(df_su[df_su["su01"] == 1], on="folio", how="inner")
    
    # Filter households that sold eggs last month (inr04d == 1)
    households_sold_eggs = households_with_land.merge(df_inr[["folio", "inr04d"]], on="folio", how="inner")
    households_sold_eggs = households_sold_eggs[households_sold_eggs["inr04d"] == 1]
    
    # Identify households with non-ag business (nna01 == 1)
    households_with_nna = oaxaca_households.merge(df_nna, on="folio", how="left")
    households_with_nna["nna01"] = households_with_nna["nna01"].fillna(2)  # Assume missing means no
    households_with_nna["has_nna"] = households_with_nna["nna01"] == 1
    
    # Merge to get all relevant households
    households_final = households_sold_eggs.merge(
        households_with_nna[["folio", "has_nna"]],
        on="folio",
        how="left"
    )
    # Fill missing has_nna as False (no non-ag business)
    households_final["has_nna"] = households_final["has_nna"].fillna(False)
    
    # Calculate average eggs sold last month among households with non-ag business
    avg_eggs_with_nna = households_final[households_final["has_nna"]]["inr04d"].mean()
    
    # Filter households without non-ag business
    households_no_nna = households_final[~households_final["has_nna"]]
    
    # Among these, find households with last month eggs sold quantity > average
    result = households_no_nna[households_no_nna["inr04d"] > avg_eggs_with_nna]
    
    # Select Household ID and last month eggs sold quantity, sort descending
    result_df = result[["folio", "inr04d"]].sort_values(by="inr04d", ascending=False)
    
    return result_df.reset_index(drop=True)