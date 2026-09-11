def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_crh = tables["ii_crh"]

    # 1. Filter Oaxaca households (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20.0]

    # 2. For each household, get the oldest member's age
    oldest_age = oaxaca_portad.groupby("folio")["edad"].max().reset_index()
    oldest_age = oldest_age.rename(columns={"edad": "oldest_age"})

    # 3. Keep only households where oldest member is at least 65
    oldest_65 = oldest_age[oldest_age["oldest_age"] >= 65]

    # 4. Households that reported a member's death in last 5 years (se01a == 1)
    se_death = df_se[df_se["se01a"] == 1.0][["folio"]]

    # 5. Merge: Oaxaca, oldest >= 65, and reported death
    eligible_folios = pd.merge(oldest_65, se_death, on="folio", how="inner")

    # 6. Get total debts + interests (crh04_2) for these households
    crh_debts = df_crh[["folio", "crh04_2"]]

    # 7. Only consider households with a reported (non-null) crh04_2
    crh_debts_nonnull = crh_debts[crh_debts["crh04_2"].notnull()]

    # 8. Compute average crh04_2 among ALL Oaxaca households with reported amounts
    oaxaca_folios = oaxaca_portad["folio"].unique()
    oaxaca_crh_debts = crh_debts[crh_debts["folio"].isin(oaxaca_folios)]
    oaxaca_crh_debts_nonnull = oaxaca_crh_debts[oaxaca_crh_debts["crh04_2"].notnull()]
    avg_debt = oaxaca_crh_debts_nonnull["crh04_2"].mean()

    # 9. For eligible households, get their crh04_2 and count those above average
    eligible_debts = pd.merge(eligible_folios, crh_debts_nonnull, on="folio", how="inner")
    count_above_avg = (eligible_debts["crh04_2"] > avg_debt).sum()

    return pd.DataFrame({"households_above_avg_debt": [int(count_above_avg)]})