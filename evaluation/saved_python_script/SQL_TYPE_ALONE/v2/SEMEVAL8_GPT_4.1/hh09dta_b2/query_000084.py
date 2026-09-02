def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]

    # 1. Households that received Liconsa Milk in the last 12 months: in03a == 1
    df_in_liconsa = df_in[df_in["in03a"] == 1.0][["folio"]].drop_duplicates()

    # 2. Households that report feeling very safe or safe at home: vlh04 == 1 or 2
    df_vlh_safe = df_vlh[df_vlh["vlh04"].isin([1.0, 2.0])][["folio"]].drop_duplicates()

    # 3. Intersection: households that satisfy both
    folios = pd.Series(np.intersect1d(df_in_liconsa["folio"].values, df_vlh_safe["folio"].values))

    # 4. For these households, get state (ent) and value of electronic devices (ah04e_2)
    # Need to get one row per household for ah04e_2 (value of electronic devices)
    # ah04e_2 is in ii_ah, which is at the individual level, but value is per household
    # We'll aggregate by folio and sum ah04e_2 per household (if multiple individuals report, sum)
    df_ah_elec = df_ah[df_ah["folio"].isin(folios)]
    df_ah_elec_sum = df_ah_elec.groupby("folio", as_index=False)["ah04e_2"].sum(min_count=1)

    # Merge with state info from ii_portad (one row per folio)
    df_portad_folio = df_portad[["folio", "ent"]].drop_duplicates()
    df_merge = df_ah_elec_sum.merge(df_portad_folio, on="folio", how="left")

    # Remove households with missing ah04e_2 (i.e., no value reported)
    df_merge = df_merge[~df_merge["ah04e_2"].isna()]

    # 5. Compute per-state average per-household value of electronic devices
    df_state_avg = df_merge.groupby("ent", as_index=False)["ah04e_2"].mean()
    df_state_avg = df_state_avg.rename(columns={"ah04e_2": "avg_electronic_value"})

    # 6. Compute overall average per-household value of electronic devices (across all selected households)
    overall_avg = df_merge["ah04e_2"].mean()

    # 7. Filter states with average above overall average
    df_above = df_state_avg[df_state_avg["avg_electronic_value"] > overall_avg]

    # 8. Map state codes to names
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
    df_above["state"] = df_above["ent"].map(state_map)

    # 9. Sort from highest to lowest average
    df_above = df_above.sort_values("avg_electronic_value", ascending=False)

    # 10. Select columns for output
    result = df_above[["state", "avg_electronic_value"]].reset_index(drop=True)

    return result