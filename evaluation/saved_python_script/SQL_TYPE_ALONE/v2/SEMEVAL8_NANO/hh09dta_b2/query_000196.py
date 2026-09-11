def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract relevant tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    ah = tables["ii_ah"]
    su = tables["ii_su"]
    
    # Filter households that use plots (su01 == 1) and lost home or business to natural disaster (se01d == 1)
    # First, get households with 'se01d' == 1 (lost viv/neg natural disaster)
    se_disaster = se[se["se01d"] == 1][["folio"]]
    
    # Filter households that use plots (su01 == 1)
    su_plots = su[su["su01"] == 1][["folio"]]
    
    # Merge to get households that satisfy both conditions
    households_disaster_plots = pd.merge(se_disaster, su_plots, on="folio", how="inner")
    
    # Filter households in portad to get demographic info
    households = portad[portad["folio"].isin(households_disaster_plots["folio"])]
    
    # Merge with 'se' to get 'se02ab_2' (year HHM died) and 'se02ca_2' (year unemployment/failure HHM)
    se_filtered = se[se["folio"].isin(households["folio"])]
    
    # Filter households where 'se02ab_2' or 'se02ca_2' indicate reported year (not DK)
    # We consider households where at least one of these is not NaN and not DK (assuming DK coded as 8)
    households_with_years = se_filtered[
        ((se_filtered["se02ab_2"] != 8) & (~se_filtered["se02ab_2"].isna())) |
        ((se_filtered["se02ca_2"] != 8) & (~se_filtered["se02ca_2"].isna()))
    ][["folio"]]
    
    # Final set of households: in portad, in disaster+plots, and reported year info
    final_households = portad[
        (portad["folio"].isin(households_with_years["folio"])) &
        (portad["folio"].isin(households_disaster_plots["folio"]))
    ]
    
    # Merge with 'ah' to get household assets info
    ah_filtered = ah[ah["folio"].isin(final_households["folio"])]
    
    # Merge with 'se' to get 'se01a' (dead HHM) info
    se_final = se[se["folio"].isin(final_households["folio"])]
    
    # Filter households that reported losing their home or business to natural disaster (se01d == 1)
    households_lost_home_biz = se_final[se_final["se01d"] == 1][["folio"]]
    
    # Merge with 'portad' to get demographic info
    households_final = portad[portad["folio"].isin(households_lost_home_biz["folio"])]
    
    # Merge with 'ii_su' to get 'su22e_1' (expense in other weight/measure)
    su_final = su[su["folio"].isin(households_final["folio"])]
    
    # Merge with 'ii_se' to get 'se02ab_2' (year HHM died) for filtering
    se_final = se[se["folio"].isin(households_final["folio"])]
    
    # Filter households with reported year info (not DK)
    households_with_years = se_final[
        ((se_final["se02ab_2"] != 8) & (~se_final["se02ab_2"].isna()))
    ][["folio"]]
    
    # Final households: in portad, reported loss to disaster, use plots, and have year info
    final_folios = portad[
        (portad["folio"].isin(households_with_years["folio"])) &
        (portad["folio"].isin(households_disaster_plots["folio"]))
    ]["folio"]
    
    # Filter 'se' for these households
    se_final = se[se["folio"].isin(final_folios)]
    # Filter households that reported losing home or business (se01d == 1)
    households_lost_home_biz = se_final[se_final["se01d"] == 1]
    
    # Get 'se02ab_2' (year HHM died) and 'se02ca_2' (year unemployment/failure HHM)
    # Filter out DK (8) and missing
    households_with_years = households_lost_home_biz[
        ((households_lost_home_biz["se02ab_2"] != 8) & (~households_lost_home_biz["se02ab_2"].isna())) |
        ((households_lost_home_biz["se02ca_2"] != 8) & (~households_lost_home_biz["se02ca_2"].isna()))
    ]
    
    # Get the set of households that satisfy all conditions
    households_final = portad[portad["folio"].isin(households_with_years["folio"])]
    
    # Merge with 'se' to get 'se01a' (dead HHM) info
    se_final = se[se["folio"].isin(households_final["folio"])]
    # Filter households that reported losing their home or business to natural disaster
    households_lost_home_biz = se_final[se_final["se01d"] == 1]
    
    # Merge with 'ii_su' to get 'su22e_1' (expense in other weight/measure)
    su_final = su[su["folio"].isin(households_final["folio"])]
    
    # Merge with 'ii_portad' to get 'edad' and 'ent' for grouping
    portad_final = portad[portad["folio"].isin(households_final["folio"])]
    
    # Calculate overall average 'se02ab_2' (year HHM died) for these households
    # Filter out DK (8) and missing
    se_for_avg = se[se["folio"].isin(households_final["folio"])]
    se_for_avg = se_for_avg[
        (se_for_avg["se02ab_2"] != 8) & (~se_for_avg["se02ab_2"].isna())
    ]
    overall_avg_seed_expense = su[
        su["folio"].isin(se_for_avg["folio"])
    ]["su22e_1"].mean()
    
    # Group by 'ent' (state) and 'edad' (age) to get household counts and mean seed expense
    # Filter households with 'su22e_1' not null
    seed_expenses = su[su["folio"].isin(households_final["folio"])]
    seed_expenses = seed_expenses[seed_expenses["su22e_1"].notna()]
    
    # Merge with portad to get 'ent' (state)
    merged = pd.merge(seed_expenses, portad[["folio", "ent"]], on="folio", how="left")
    
    # Group by 'ent' (state)
    group = merged.groupby("ent").agg(
        household_count=pd.NamedAgg(column="folio", aggfunc="count"),
        mean_seed_expense=pd.NamedAgg(column="su22e_1", aggfunc="mean")
    ).reset_index()
    
    # Filter states with at least 10 households
    filtered = group[group["household_count"] >= 10]
    
    # Determine which states have mean seed expense above overall average
    above_avg = filtered[filtered["mean_seed_expense"] > overall_avg_seed_expense]
    
    # Map 'ent' codes to state names
    ent_map = {
        2: "Baja California",
        3: "Baja California Sur",
        4: "Campeche",
        5: "Coahuila",
        6: "Colima",
        7: "Chiapas",
        9: "Distrito Federal",
        10: "Durango",
        11: "Guanajuato",
        12: "Guerrero",
        13: "Hidalgo",
        14: "Jalisco",
        15: "Estado de México",
        16: "Michoacán",
        17: "Morelos",
        18: "Nayarit",
        19: "Nuevo León",
        20: "Oaxaca",
        21: "Puebla",
        22: "Querétaro",
        25: "Sinaloa",
        26: "Sonora",
        28: "Tamaulipas",
        29: "Tlaxcala",
        30: "Veracruz",
        31: "Yucatán",
        32: "Zacatecas"
    }
    above_avg["state"] = above_avg["ent"].map(ent_map)
    # Select relevant columns and sort by mean_seed_expense descending
    result = above_avg[["state", "household_count", "mean_seed_expense"]]
    result = result.sort_values(by="mean_seed_expense", ascending=False).reset_index(drop=True)
    return result