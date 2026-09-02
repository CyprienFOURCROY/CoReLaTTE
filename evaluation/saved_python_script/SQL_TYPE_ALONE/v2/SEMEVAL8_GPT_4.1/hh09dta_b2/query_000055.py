def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_crh = tables["ii_crh"]
    df_ah = tables["ii_ah"]

    # 1. Identify households with at least one adult (18+)
    df_adults = df_portad[df_portad["edad"] >= 18]
    hh_with_adult = set(df_adults["folio"].unique())

    # 2. Households that own/share a non-ag business (nna01 == 1)
    df_nna_yes = df_nna[df_nna["nna01"] == 1]
    hh_with_business = set(df_nna_yes["folio"].unique())

    # 3. Households that did not incur debts in the last 12 months (crh02_1 == 2)
    df_crh_no_debt = df_crh[df_crh["crh02_1"] == 2]
    hh_no_debt = set(df_crh_no_debt["folio"].unique())

    # 4. Households that reported a value for washing machine/stove assets (ah04f_1 == 1 and ah04f_2 not null)
    df_ah_valid = df_ah[(df_ah["ah04f_1"] == 1) & (df_ah["ah04f_2"].notnull())]
    # Only keep one record per household (since asset value is at household level)
    df_ah_valid = df_ah_valid.sort_values("ah04f_2", ascending=False).drop_duplicates("folio")
    hh_with_asset = set(df_ah_valid["folio"].unique())

    # 5. Intersection of all criteria
    eligible_hh = hh_with_adult & hh_with_business & hh_no_debt & hh_with_asset

    # 6. Filter to eligible households
    df_ah_eligible = df_ah_valid[df_ah_valid["folio"].isin(eligible_hh)].copy()

    # 7. Merge with state info
    df_portad_hh = df_portad.drop_duplicates("folio")[["folio", "ent"]]
    df_ah_eligible = df_ah_eligible.merge(df_portad_hh, on="folio", how="left")

    # 8. Compute national average
    national_avg = df_ah_eligible["ah04f_2"].mean()

    # 9. Compute state averages
    state_avg = df_ah_eligible.groupby("ent", as_index=False)["ah04f_2"].mean()

    # 10. Filter states above national average and sort
    state_avg_above = state_avg[state_avg["ah04f_2"] > national_avg].sort_values("ah04f_2", ascending=False)

    # 11. Map state codes to names
    state_map = {
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
    state_avg_above["state"] = state_avg_above["ent"].map(state_map)
    state_avg_above = state_avg_above[["state", "ah04f_2"]].rename(columns={"ah04f_2": "avg_wash_machine_stove_value"}).reset_index(drop=True)

    return state_avg_above