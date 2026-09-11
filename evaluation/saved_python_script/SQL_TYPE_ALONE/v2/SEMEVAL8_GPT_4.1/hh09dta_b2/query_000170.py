def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]

    # 1. Get Oaxaca households with at least one adult (age 18+)
    oaxaca_adults = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)]
    oaxaca_adult_folios = oaxaca_adults["folio"].unique()

    # 2. Of these, select households that produced/sold crafts in last 12 months (inr02f == 1)
    oaxaca_inr = df_inr[df_inr["folio"].isin(oaxaca_adult_folios)]
    crafts_folios = oaxaca_inr[oaxaca_inr["inr02f"] == 1.0]["folio"].unique()

    # 3. For all Oaxaca households with at least one adult that own electronic devices with reported values
    #    (ah03e == 1 and ah04e_1 == 1 and ah04e_2 not null)
    oaxaca_ah = df_ah[df_ah["folio"].isin(oaxaca_adult_folios)]
    oaxaca_ah_electronics = oaxaca_ah[
        (oaxaca_ah["ah03e"] == 1.0) & (oaxaca_ah["ah04e_1"] == 1.0) & (oaxaca_ah["ah04e_2"].notnull())
    ]
    # Sum value per household (in case of multiple rows per folio)
    electronics_value_per_folio = oaxaca_ah_electronics.groupby("folio")["ah04e_2"].sum()

    # 4. Compute average value for these Oaxaca households
    avg_electronics_value = electronics_value_per_folio.mean()

    # 5. For Oaxaca households with at least one adult that produced/sold crafts in last 12 months,
    #    get those with total reported value of electronic devices above the average
    crafts_ah = oaxaca_ah[
        (oaxaca_ah["folio"].isin(crafts_folios)) &
        (oaxaca_ah["ah03e"] == 1.0) & (oaxaca_ah["ah04e_1"] == 1.0) & (oaxaca_ah["ah04e_2"].notnull())
    ]
    crafts_electronics_value_per_folio = crafts_ah.groupby("folio")["ah04e_2"].sum()
    above_avg_folios = crafts_electronics_value_per_folio[crafts_electronics_value_per_folio > avg_electronics_value].index

    # 6. Count number of such households
    result = len(above_avg_folios)

    return pd.DataFrame({"num_households": [result]})