def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_vlh = tables["ii_vlh"]

    # 1. Respondents aged 30 and older
    df_portad_30 = df_portad[df_portad["edad"] >= 30]

    # 2. Households that produced or sold crafts in the last 12 months (inr02f == 1)
    df_inr_crafts = df_inr[df_inr["inr02f"] == 1]

    # 3. Respondents who report feeling safe or very safe at home (vlh04 == 1 or 2)
    df_vlh_safe = df_vlh[df_vlh["vlh04"].isin([1, 2])]

    # 4. Merge all three on folio (household id)
    # First, merge portad and inr on folio and ls (individual id)
    df1 = df_portad_30.merge(df_inr_crafts[["folio", "ls"]], on=["folio", "ls"], how="inner")
    # Then, merge with vlh on folio (since vlh is at household level)
    df2 = df1.merge(df_vlh_safe[["folio"]], on="folio", how="inner")

    # 5. Group by state and count respondents
    state_counts = df2.groupby("ent").size().reset_index(name="num_respondents")

    # 6. Compute average across states
    avg = state_counts["num_respondents"].mean()

    # 7. Filter states with at least the average
    result = state_counts[state_counts["num_respondents"] >= avg].copy()

    # 8. Sort from highest to lowest
    result = result.sort_values("num_respondents", ascending=False).reset_index(drop=True)

    # 9. Map state codes to names
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
    result["state"] = result["ent"].map(state_map)
    result = result[["state", "num_respondents"]]

    return result