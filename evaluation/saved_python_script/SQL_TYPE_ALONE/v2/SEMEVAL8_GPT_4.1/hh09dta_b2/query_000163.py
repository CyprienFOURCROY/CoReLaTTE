def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # Adults (18+), in Oaxaca (ent==20)
    adults_oaxaca = df_portad[(df_portad["edad"] >= 18) & (df_portad["ent"] == 20.0)]

    # Households that own a motor vehicle (ah03d==1)
    ah_mv = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # Households with reported total debts+interest (crh04_1==1, crh04_2 not null)
    crh_debt = df_crh[(df_crh["crh04_1"] == 1.0) & (~df_crh["crh04_2"].isna())][["folio", "crh04_2"]]

    # Restrict to Oaxaca households
    oaxaca_folios = set(adults_oaxaca["folio"].unique())
    ah_mv_oax = ah_mv[ah_mv["folio"].isin(oaxaca_folios)]
    crh_debt_oax = crh_debt[crh_debt["folio"].isin(oaxaca_folios)]

    # Compute Oaxaca average debt+interest (among those with reported values)
    oax_debt_avg = crh_debt_oax["crh04_2"].mean()

    # Households with debt+interest > average
    crh_debt_oax_gt_avg = crh_debt_oax[crh_debt_oax["crh04_2"] > oax_debt_avg]

    # Households that satisfy both: own motor vehicle AND debt+interest > avg
    eligible_folios = set(ah_mv_oax["folio"]).intersection(set(crh_debt_oax_gt_avg["folio"]))

    # Adults in Oaxaca in those households
    adults_in_eligible = adults_oaxaca[adults_oaxaca["folio"].isin(eligible_folios)]

    count = len(adults_in_eligible)

    return pd.DataFrame({"num_adults": [count]})