def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_inr = tables["ii_inr"]

    # Step 1: Households with at least one member aged 18 or older
    df_adult = df_portad[df_portad["edad"] >= 18]
    hh_with_adult = df_adult["folio"].unique()

    # Step 2: Households that own poultry (ah03m == 1)
    df_ah_poultry = df_ah[df_ah["ah03m"] == 1]
    hh_with_poultry = df_ah_poultry["folio"].unique()

    # Step 3: Intersection: households with at least one adult and own poultry
    hh_adult_poultry = np.intersect1d(hh_with_adult, hh_with_poultry)

    # Step 4: For these households, get their state
    df_portad_hh = df_portad[df_portad["folio"].isin(hh_adult_poultry)]
    # Get one row per household for state (assuming state is the same for all members)
    df_hh_state = df_portad_hh.groupby("folio", as_index=False).first()[["folio", "ent"]]

    # Step 5: Of these, how many produced/sold dairy in last 12 months (inr02a == 1)
    df_inr_hh = df_inr[df_inr["folio"].isin(hh_adult_poultry)]
    hh_dairy = df_inr_hh[df_inr_hh["inr02a"] == 1]["folio"].unique()

    # Step 6: Aggregate by state
    df_hh_state["has_dairy"] = df_hh_state["folio"].isin(hh_dairy)
    result = df_hh_state.groupby("ent").agg(
        households_with_adult_and_poultry=("folio", "nunique"),
        households_with_adult_poultry_and_dairy=("has_dairy", "sum")
    ).reset_index()

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
    result["state"] = result["ent"].map(state_map)
    result = result[["ent", "state", "households_with_adult_and_poultry", "households_with_adult_poultry_and_dairy"]]
    return result