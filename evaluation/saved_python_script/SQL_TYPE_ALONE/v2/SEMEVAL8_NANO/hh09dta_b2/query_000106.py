def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]
    
    # Filter households from Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20]
    
    # Merge with ii_crh on 'folio'
    merged_crh = pd.merge(oaxaca_households, df_crh, on="folio", how="inner")
    
    # Filter households with reported total debts (crh04_1 == 1)
    households_with_debt = merged_crh[merged_crh["crh04_1"] == 1]
    
    # Calculate average total debts + interests (crh04_2) among these households
    # Exclude NaN values
    avg_debt = households_with_debt["crh04_2"].dropna().mean()
    
    # Filter households with total debts above the average
    above_avg_debt = households_with_debt[households_with_debt["crh04_2"] > avg_debt]
    
    # Further filter households that received a positive amount from 'in02a12' (amount received directly from Other Government Program)
    # 'in02a12' is float, positive means > 0
    households_positive_other_gov = above_avg_debt[above_avg_debt["in02a12"] > 0]
    
    # Count unique households (by 'folio')
    count_households = households_positive_other_gov["folio"].nunique()
    
    # Return as DataFrame
    return pd.DataFrame(
        {"household_count": [count_households]}
    )