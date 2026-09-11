def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_se = tables["ii_se"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_hh = df_portad[df_portad["ent"] == 20]
    
    # Filter households with oldest member at least 65 years old
    hh_age_65_plus = oaxaca_hh[oaxaca_hh["edad"] >= 65]
    
    # Filter households that reported a household member's death in last five years
    # 'se01a' indicates if HH: dead HHM in last 5 years (1: Yes, 3: No)
    hh_death_reported = df_se[
        (df_se["folio"].isin(hh_age_65_plus["folio"])) &
        (df_se["se01a"] == 1)
    ]
    
    # Get the set of folios that meet all criteria
    folios_filtered = hh_death_reported["folio"].unique()
    
    # Filter households in the filtered folios
    hh_final = hh_age_65_plus[hh_age_65_plus["folio"].isin(folios_filtered)]
    
    # Get debts plus interests in pesos for these households
    df_crh_filtered = df_crh[df_crh["folio"].isin(hh_final["folio"])]
    
    # Filter out entries with missing 'crh04_2' (amount in pesos)
    crh_debts = df_crh_filtered[~df_crh_filtered["crh04_2"].isna()]
    
    # Calculate the average amount of debts plus interests
    avg_debt_amount = crh_debts["crh04_2"].mean()
    
    # Count households with debts > average
    # First, get unique folios with debts > average
    folios_debt_gt_avg = crh_debts[crh_debts["crh04_2"] > avg_debt_amount]["folio"].unique()
    
    # Count how many of these folios are in the final filtered households
    count = hh_final[hh_final["folio"].isin(folios_debt_gt_avg)].shape[0]
    
    return pd.DataFrame({"count": [count]})