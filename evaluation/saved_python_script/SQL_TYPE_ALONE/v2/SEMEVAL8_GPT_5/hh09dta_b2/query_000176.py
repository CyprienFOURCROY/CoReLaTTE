import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()
    df_su = tables["ii_su"].copy()

    # Households that use a plot/land for farming
    su_use = df_su[df_su["su01"] == 1.0][["folio"]].drop_duplicates()

    # Households with recorded total debt (debts + interest)
    crh_debt = df_crh[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna())][["folio", "crh04_2"]]

    # Merge criteria: use land and have recorded debt
    hh = su_use.merge(crh_debt, on="folio", how="inner")

    if hh.empty:
        return pd.DataFrame(columns=["ent", "state", "avg_total_debt"])

    # Overall average debt across the group
    overall_avg = hh["crh04_2"].mean()

    # Keep only households whose debt exceeds the overall average
    hh_high = hh[hh["crh04_2"] > overall_avg]

    if hh_high.empty:
        return pd.DataFrame(columns=["ent", "state", "avg_total_debt"])

    # Map households to state
    ent_per_folio = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])
    hh_high = hh_high.merge(ent_per_folio, on="folio", how="left")
    hh_high = hh_high[hh_high["ent"].notna()]

    if hh_high.empty:
        return pd.DataFrame(columns=["ent", "state", "avg_total_debt"])

    # State-level average of debts among above-average households
    state_avg = (
        hh_high.groupby("ent", as_index=False)["crh04_2"]
        .mean()
        .rename(columns={"crh04_2": "avg_total_debt"})
    )

    # Filter states with average > 10,000 pesos
    state_avg = state_avg[state_avg["avg_total_debt"] > 10000]

    if state_avg.empty:
        return pd.DataFrame(columns=["ent", "state", "avg_total_debt"])

    # Map state codes to names
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

    state_avg["ent"] = state_avg["ent"].astype("Int64")
    state_avg["state"] = state_avg["ent"].map(ent_to_state)

    # Order by highest average
    state_avg = state_avg.sort_values(by="avg_total_debt", ascending=False).reset_index(drop=True)

    return state_avg[["ent", "state", "avg_total_debt"]]