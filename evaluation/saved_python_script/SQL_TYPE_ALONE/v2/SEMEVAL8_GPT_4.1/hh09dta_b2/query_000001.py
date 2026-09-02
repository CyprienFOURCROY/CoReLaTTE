def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Merge to get state info
    df = df_vlh.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Only households who answered Yes to knowing a family/friend robbed in last 5 years (vlh08a == 1)
    df_yes = df[df["vlh08a"] == 1]

    # Group by state, count households
    state_counts = df_yes.groupby("ent")["folio"].nunique().reset_index(name="n_households")

    # Only states with at least 5 such households
    valid_states = state_counts[state_counts["n_households"] >= 5]["ent"]

    # Filter to those states
    df_valid = df_yes[df_yes["ent"].isin(valid_states)]

    # Compute averages for "Feel safe at home?" (vlh04) and "Leave lights on as a security method?" (vlh06)
    # Only use non-null values for the averages
    result = (
        df_valid.groupby("ent")
        .agg(
            avg_feel_safe_at_home=("vlh04", lambda x: np.nanmean(x)),
            avg_leave_lights_on=("vlh06", lambda x: np.nanmean(x)),
            n_households=("folio", "nunique")
        )
        .reset_index()
    )

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

    # Order from safest to least safe (lowest avg_feel_safe_at_home to highest; 1=Very safe, 4=Very unsafe)
    result = result.sort_values("avg_feel_safe_at_home", ascending=True)

    # Reorder columns
    result = result[["state", "avg_feel_safe_at_home", "avg_leave_lights_on", "n_households"]].reset_index(drop=True)

    return result