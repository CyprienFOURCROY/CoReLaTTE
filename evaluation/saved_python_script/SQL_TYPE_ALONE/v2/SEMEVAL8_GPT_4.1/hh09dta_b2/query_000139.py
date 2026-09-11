def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Households with at least one senior (>=70) and at least one child (<12)
    seniors = df_portad[df_portad["edad"] >= 70].groupby("folio").size().rename("senior_count")
    children = df_portad[df_portad["edad"] < 12].groupby("folio").size().rename("child_count")
    hh_with_senior_and_child = pd.DataFrame({"senior": seniors, "child": children}).dropna()

    # Only households with at least one senior and one child
    hh_with_senior_and_child = hh_with_senior_and_child[
        (hh_with_senior_and_child["senior"] >= 1) & (hh_with_senior_and_child["child"] >= 1)
    ]
    hh_folios = set(hh_with_senior_and_child.index)

    # Households that received Liconsa milk in the last 12 months (in03a == 1)
    df_in_liconsa = df_in[df_in["in03a"] == 1]
    liconsa_folios = set(df_in_liconsa["folio"])

    # Intersection: households with both conditions
    target_folios = hh_folios & liconsa_folios

    # Get state for each household
    df_portad_hh = df_portad.drop_duplicates("folio")[["folio", "ent"]]
    df_target = df_portad_hh[df_portad_hh["folio"].isin(target_folios)]

    # Count households per state
    state_counts = df_target.groupby("ent").size().rename("household_count").reset_index()

    # National average
    national_avg = state_counts["household_count"].mean()

    # States above national average
    above_avg = state_counts[state_counts["household_count"] > national_avg].copy()

    # Map state codes to names
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
    above_avg["state"] = above_avg["ent"].map(state_map)
    above_avg = above_avg[["state", "household_count"]].reset_index(drop=True)

    return above_avg