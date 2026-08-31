import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"].copy()
    df_inr = tables["ii_inr"].copy()

    # Households that use a plot/land and did not produce/sell honey in last 12 months
    sel_su = df_su.loc[df_su["su01"] == 1.0, ["folio"]]
    sel_inr = df_inr.loc[df_inr["inr02i"] == 3.0, ["folio"]]
    sel_households = sel_su.merge(sel_inr, on="folio", how="inner").drop_duplicates()

    # Join with individuals to get state and ages for those households
    df_join = df_portad.merge(sel_households, on="folio", how="inner")

    # Aggregate by state
    grouped = df_join.groupby("ent", dropna=True)
    households_count = grouped["folio"].nunique()
    avg_age = grouped["edad"].mean()

    df_state = pd.DataFrame({
        "households": households_count,
        "avg_age": avg_age
    }).reset_index()

    # Filter states with at least 40 such households
    df_state = df_state[df_state["households"] >= 40]

    # Overall average age across all respondents
    overall_avg = df_portad["edad"].mean()

    # Keep states where average age is below overall average
    df_state = df_state[df_state["avg_age"] < overall_avg]

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
        32: "Zacatecas",
    }
    df_state["ent_code"] = df_state["ent"].astype("Int64")
    df_state["state_name"] = df_state["ent_code"].map(state_map)

    # Order from lowest to highest average age
    df_state = df_state.sort_values(by="avg_age", ascending=True).reset_index(drop=True)

    return df_state[["ent_code", "state_name", "households", "avg_age"]]