def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]
    df_portad = tables["ii_portad"]

    # 1. Households that reported producing/selling fattening animals in last 12 months
    fattening_hh = df_inr[df_inr["inr02j"] == 1][["folio"]].drop_duplicates()

    # 2. Merge with asset value of bull/cow (ah04j_2) and only keep those with a value
    df_ah_bull = df_ah[["folio", "ah04j_1", "ah04j_2"]]
    # Only keep if value is known (ah04j_1 == 1) and value is not null
    df_ah_bull = df_ah_bull[(df_ah_bull["ah04j_1"] == 1) & (df_ah_bull["ah04j_2"].notnull())]

    # Merge to get only relevant households
    fattening_bull = pd.merge(fattening_hh, df_ah_bull, on="folio", how="inner")

    # 3. Compute average bull/cow asset value among these households
    avg_bull_value = fattening_bull["ah04j_2"].mean()

    # 4. Keep only households whose bull/cow asset value exceeds the average
    fattening_bull_above_avg = fattening_bull[fattening_bull["ah04j_2"] > avg_bull_value]

    # 5. Get the list of folios (households) that meet the above criteria
    folios_above_avg = fattening_bull_above_avg["folio"].unique()

    # 6. For these households, count number of adults (age >= 18) per household
    df_portad_adults = df_portad[df_portad["edad"] >= 18]
    df_adults_in_folios = df_portad_adults[df_portad_adults["folio"].isin(folios_above_avg)]

    # Group by folio and count adults
    adults_per_hh = df_adults_in_folios.groupby("folio").size()

    # 7. Compute the average number of adults per household
    if len(adults_per_hh) == 0:
        avg_adults = float('nan')
    else:
        avg_adults = adults_per_hh.mean()

    return pd.DataFrame({"average_adults_per_household": [avg_adults]})