def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one member aged 18 or older
    hh_18plus = oaxaca_households[oaxaca_households["edad"] >= 18.0]["folio"].unique()

    # 3. Households that use a plot/land for cultivation (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1.0]["folio"].unique()

    # 4. Households where individual with ID 1 reports ownership of a motor vehicle (ah03d == 1 for ls == 1)
    ah_ind1 = df_ah[(df_ah["ls"] == 1.0) & (df_ah["ah03d"] == 1.0)]
    hh_motor_vehicle = ah_ind1["folio"].unique()

    # 5. Intersection of all three conditions
    eligible_folios = set(hh_18plus) & set(su_plot) & set(hh_motor_vehicle)

    return pd.DataFrame({"folio": sorted(eligible_folios)})