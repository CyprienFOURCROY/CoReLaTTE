def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_vlh = tables["ii_vlh"]

    # 1. Households that feel unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]]

    # 2. Households with illness/accident/hospitalization in last 5 years (se01b == 1)
    df_se_ill = df_se[df_se["se01b"] == 1.0][["folio"]]

    # 3. Intersection: households that meet both criteria
    folios_unsafe = set(df_vlh_unsafe["folio"])
    folios_ill = set(df_se_ill["folio"])
    folios_both = folios_unsafe & folios_ill

    # 4. Get state for each household
    df_portad_hh = df_portad.drop_duplicates("folio")[["folio", "ent"]]
    df_both = df_portad_hh[df_portad_hh["folio"].isin(folios_both)]

    # 5. Count households per state
    state_counts = df_both.groupby("ent").size().reset_index(name="num_households")

    # 6. Filter states with at least 50 such households
    state_counts = state_counts[state_counts["num_households"] >= 50]

    # 7. Map state codes to names
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
    state_counts["state"] = state_counts["ent"].map(state_map)
    state_counts = state_counts[["state", "num_households"]].sort_values("num_households", ascending=False).reset_index(drop=True)
    return state_counts