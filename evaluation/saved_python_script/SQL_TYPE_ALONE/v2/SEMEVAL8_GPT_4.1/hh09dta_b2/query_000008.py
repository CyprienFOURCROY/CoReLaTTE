def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_ah = tables["ii_ah"]

    # Households that own a motor vehicle: ah03d == 1
    df_veh = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # Merge with crh to get total household debt (including interest)
    df_debt = df_crh.merge(df_veh, on="folio", how="inner")

    # Only households with reported debt values: crh04_1 == 1 and crh04_2 not null
    df_debt = df_debt[(df_debt["crh04_1"] == 1.0) & (~df_debt["crh04_2"].isna())]

    # Merge with portad to get state
    df_debt = df_debt.merge(df_portad[["folio", "ent"]].drop_duplicates(), on="folio", how="left")

    # Compute overall average
    overall_avg = df_debt["crh04_2"].mean()

    # Compute state averages
    state_avg = df_debt.groupby("ent")["crh04_2"].mean().reset_index()

    # Only states where average exceeds overall average
    state_avg = state_avg[state_avg["crh04_2"] > overall_avg]

    # Top 10 states by average debt
    state_avg = state_avg.sort_values("crh04_2", ascending=False).head(10)

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
    state_avg["state"] = state_avg["ent"].map(state_map)
    state_avg = state_avg.rename(columns={"crh04_2": "average_total_household_debt"})
    state_avg = state_avg[["ent", "state", "average_total_household_debt"]].reset_index(drop=True)
    return state_avg