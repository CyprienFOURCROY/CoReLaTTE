import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh18a"]].copy()

    # Aggregate per household
    hh_vlh = df_vlh.groupby("folio", as_index=False, dropna=False)["vlh18a"].max()

    # Keep households with at least one incident since 2005
    hh_incidents = hh_vlh[hh_vlh["vlh18a"] > 0].copy()
    if hh_incidents.empty:
        return pd.DataFrame(columns=["ent", "state", "n_households_above_avg"])

    overall_avg = hh_incidents["vlh18a"].mean()

    # Households above overall average
    hh_above = hh_incidents[hh_incidents["vlh18a"] > overall_avg].copy()

    # Map households to states (one state per household)
    hh_state = df_portad.dropna(subset=["ent"]).groupby("folio", as_index=False)["ent"].first()
    hh_state["ent"] = hh_state["ent"].astype(int)

    hh_above_state = hh_above.merge(hh_state, on="folio", how="left").dropna(subset=["ent"])
    if hh_above_state.empty:
        return pd.DataFrame(columns=["ent", "state", "n_households_above_avg"])

    # Count households per state
    counts = (
        hh_above_state.groupby("ent")
        .size()
        .reset_index(name="n_households_above_avg")
        .sort_values(["n_households_above_avg", "ent"], ascending=[False, True])
        .head(5)
    )

    # Map state names
    ent_to_state = {
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
    counts["state"] = counts["ent"].map(ent_to_state)

    return counts[["ent", "state", "n_households_above_avg"]]