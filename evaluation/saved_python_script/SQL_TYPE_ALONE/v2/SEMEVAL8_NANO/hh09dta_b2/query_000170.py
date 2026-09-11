def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract relevant tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    ah = tables["ii_ah"]
    ah_enriched = tables["ii_ah_enriched"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Filter households with at least one adult (edad >= 18)
    adults = oaxaca_households[oaxaca_households["edad"] >= 18]
    households_with_adults = adults["folio"].unique()
    
    # Filter households that produced or sold crafts in last 12 months (inr02f == 1)
    inr_crafts = inr[(inr["folio"].isin(households_with_adults)) & (inr["inr02f"] == 1)]
    households_crafts = inr_crafts["folio"].unique()
    
    # Filter households with at least one adult that produced or sold crafts
    households_crafts_set = set(households_crafts)
    households_with_adults_crafts = set(households_with_adults).intersection(households_crafts_set)
    
    # Get household IDs with at least one adult (age >= 18) and crafts activity
    households_with_adults_crafts_df = portad[portad["folio"].isin(households_with_adults_crafts)]
    
    # Filter households that own electronic devices with reported values
    households_with_electronics = ah_enriched[
        (ah_enriched["folio"].isin(households_with_adults_crafts))
        & (ah_enriched["ah03e"] == 1)
    ]
    
    # Calculate the average reported value of electronic devices among households that own them
    electronics_values = []
    for _, row in households_with_electronics.iterrows():
        values = []
        for col in [
            "ah04e_1", "ah04e_2",
            "ah04f_1", "ah04f_2",
            "ah04g_1", "ah04g_2",
            "ah04h_1", "ah04h_2",
            "ah04i_1", "ah04i_2",
            "ah04j_1", "ah04j_2",
            "ah04k_1", "ah04k_2",
            "ah04l_1", "ah04l_2",
            "ah04m_1", "ah04m_2",
            "ah04n_1", "ah04n_2"
        ]:
            val = row.get(col, pd.NA)
            if pd.notna(val) and val != 8:
                values.append(val)
        if values:
            electronics_values.extend(values)
    if electronics_values:
        avg_electronics_value = sum(electronics_values) / len(electronics_values)
    else:
        avg_electronics_value = float('nan')
    
    # Filter households with electronic devices with reported value above the average
    def has_value_above_avg(row):
        for col in [
            "ah04e_1", "ah04e_2",
            "ah04f_1", "ah04f_2",
            "ah04g_1", "ah04g_2",
            "ah04h_1", "ah04h_2",
            "ah04i_1", "ah04i_2",
            "ah04j_1", "ah04j_2",
            "ah04k_1", "ah04k_2",
            "ah04l_1", "ah04l_2",
            "ah04m_1", "ah04m_2",
            "ah04n_1", "ah04n_2"
        ]:
            val = row.get(col, pd.NA)
            if pd.notna(val) and val != 8:
                if val > avg_electronics_value:
                    return True
        return False
    
    households_above_avg = households_with_electronics[
        households_with_electronics.apply(has_value_above_avg, axis=1)
    ]["folio"].unique()
    
    # Count households that meet all criteria
    count = len(households_above_avg)
    
    return pd.DataFrame({"count": [count]})