def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_su = tables["ii_su"]

    # Households that own a motor vehicle (ah03d == 1)
    df_veh = df_ah[df_ah["ah03d"] == 1][["folio"]].drop_duplicates()

    # Merge with portad to get state
    df_veh_state = pd.merge(df_veh, df_portad[["folio", "ent"]], on="folio", how="left")

    # Count households with a motor vehicle per state
    veh_counts = df_veh_state.groupby("ent")["folio"].nunique().reset_index(name="num_households_with_vehicle")

    # Filter states with at least 20 such households
    eligible_states = veh_counts[veh_counts["num_households_with_vehicle"] >= 20]["ent"]

    # Households that use a plot/land for farming/vegetable (su01 == 1)
    df_farm = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Merge with portad to get state
    df_farm_state = pd.merge(df_farm, df_portad[["folio", "ent"]], on="folio", how="left")

    # Count households that use a plot per state
    farm_counts = df_farm_state.groupby("ent")["folio"].nunique().reset_index(name="num_households_with_farm")

    # For eligible states, count number of households that both own a motor vehicle and use a plot
    df_veh_farm = pd.merge(df_veh, df_farm, on="folio", how="inner")
    df_veh_farm_state = pd.merge(df_veh_farm, df_portad[["folio", "ent"]], on="folio", how="left")
    both_counts = df_veh_farm_state.groupby("ent")["folio"].nunique().reset_index(name="num_households_with_both")

    # Filter to eligible states only
    both_counts = both_counts[both_counts["ent"].isin(eligible_states)]

    # Compute average number of households with both across eligible states
    avg_both = both_counts["num_households_with_both"].mean()

    # Select states with above-average number of households with both
    result = both_counts[both_counts["num_households_with_both"] > avg_both].copy()

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
    result = result[["ent", "state", "num_households_with_both"]].reset_index(drop=True)
    return result