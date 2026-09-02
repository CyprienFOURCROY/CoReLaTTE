def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_su = tables["ii_su"]

    # 1. Households in Oaxaca (20) or Puebla (21)
    df_portad_sub = df_portad[df_portad["ent"].isin([20.0, 21.0])]

    # 2. Households that use a plot/land for sowing/farming (su01 == 1)
    df_su_sub = df_su[df_su["su01"] == 1.0]

    # 3. Households in both (merge on folio)
    folios_ok = set(df_portad_sub["folio"]).intersection(df_su_sub["folio"])
    df_portad_sub = df_portad_sub[df_portad_sub["folio"].isin(folios_ok)]
    df_su_sub = df_su_sub[df_su_sub["folio"].isin(folios_ok)]

    # 4. Households with at least one adult (age >= 18)
    adults = df_portad_sub[df_portad_sub["edad"] >= 18.0]
    folios_with_adult = set(adults["folio"])
    
    # 5. Households with at least one member who owns a motor vehicle (ah03d == 1)
    df_ah_sub = df_ah[df_ah["folio"].isin(folios_ok)]
    owns_motor_vehicle = df_ah_sub[df_ah_sub["ah03d"] == 1.0]
    folios_with_motor_vehicle = set(owns_motor_vehicle["folio"])

    # 6. Households that satisfy all three conditions
    folios_final = folios_ok & folios_with_adult & folios_with_motor_vehicle

    # 7. Compute average su239 among land-using households in Oaxaca/Puebla
    df_su_land = df_su[(df_su["folio"].isin(folios_ok))]
    avg_su239 = df_su_land["su239"].mean(skipna=True)

    # 8. Households with su239 > avg_su239
    df_su_final = df_su[(df_su["folio"].isin(folios_final))]
    df_su_final = df_su_final[df_su_final["su239"].notna()]
    df_su_final = df_su_final[df_su_final["su239"] > avg_su239]

    # 9. Count unique households
    n_households = df_su_final["folio"].nunique()

    return pd.DataFrame({"n_households": [n_households]})