def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]

    # Households that use a plot/land for farming: su01 == 1
    su_farming = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Households that own poultry: ah03m == 1
    ah_poultry = df_ah[df_ah["ah03m"] == 1][["folio"]].drop_duplicates()

    # Intersection: households that both use land for farming and own poultry
    common_folios = pd.merge(su_farming, ah_poultry, on="folio")

    # For these households, get all individuals from ii_portad
    portad_common = pd.merge(df_portad, common_folios, on="folio")

    # Compute mean age per household
    hh_mean_age = portad_common.groupby("folio")["edad"].mean().reset_index(name="mean_age")

    # Get state for each household (take first occurrence per folio)
    folio_ent = portad_common.groupby("folio")["ent"].first().reset_index()

    # Merge mean age and state
    hh_info = pd.merge(hh_mean_age, folio_ent, on="folio")

    # Compute overall average of household mean ages
    overall_avg = hh_info["mean_age"].mean()

    # For each state, get number of such households and state-level average of household mean age
    state_stats = (
        hh_info.groupby("ent")
        .agg(num_households=("folio", "nunique"), state_avg_age=("mean_age", "mean"))
        .reset_index()
    )

    # Filter: at least 25 households and state-level avg age > overall avg
    filtered = state_stats[(state_stats["num_households"] >= 25) & (state_stats["state_avg_age"] > overall_avg)]

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
    filtered["state"] = filtered["ent"].map(state_map)

    # Sort by state-level average age descending
    result = filtered.sort_values("state_avg_age", ascending=False)[
        ["state", "num_households", "state_avg_age"]
    ].reset_index(drop=True)

    return result