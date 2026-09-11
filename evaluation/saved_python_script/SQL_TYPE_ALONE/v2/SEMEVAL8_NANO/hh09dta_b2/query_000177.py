def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]
    df_portad = tables["ii_portad"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20]
    
    # Merge with ii_in to get household info
    in_merged = pd.merge(oaxaca_households, df_in, on="folio", how="inner")
    
    # Filter households with total debts + interests (crh04_1) reported as a numeric value
    # and total debts+interests in pesos (crh04_2) is positive
    crh_filtered = df_crh[
        (df_crh["crh04_1"].notna()) &
        (df_crh["crh04_1"] != 8) &  # Exclude DK
        (df_crh["crh04_2"] > 0)
    ]
    
    # Merge to get debts info
    merged = pd.merge(in_merged, crh_filtered[["folio", "crh04_2"]], on="folio", how="inner")
    
    # Calculate average of crh04_2 among households in other states with similar conditions
    other_states_crh = df_crh[
        (df_crh["crh04_1"].notna()) &
        (df_crh["crh04_1"] != 8) &
        (df_crh["crh04_2"] > 0)
    ]
    # Exclude households in Oaxaca
    other_states_crh = other_states_crh[
        ~other_states_crh["folio"].isin(oaxaca_households["folio"])
    ]
    avg_other_states = other_states_crh["crh04_2"].mean()
    
    # Filter Oaxaca households with crh04_2 >= average of other states
    result = merged[merged["crh04_2"] >= avg_other_states]
    
    # Select relevant columns
    result = result[["folio", "crh04_2", "in02a12"]]
    result = result.rename(columns={"crh04_2": "total_debts_interests", "in02a12": "received_amount"})
    
    return result.reset_index(drop=True)