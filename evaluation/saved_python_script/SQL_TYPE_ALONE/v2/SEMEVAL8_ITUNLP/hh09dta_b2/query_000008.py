import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_ah = tables["ii_ah"]

    # Households with reported total debt (including interest)
    crh = df_crh[["folio", "crh04_1", "crh04_2"]].copy()
    crh_reported = crh[(crh["crh04_1"] == 1.0) & (crh["crh04_2"].notna())].copy()

    # Overall average across all households with reported debt values
    overall_avg = crh_reported["crh04_2"].mean()

    # Households that own a motor vehicle
    motor_households = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # Intersect with households with reported debt values
    hv = motor_households.merge(crh_reported[["folio", "crh04_2"]], on="folio", how="inner")

    # Map households to states
    folio_state = df_portad[["folio", "ent"]].dropna(subset=["ent"]).drop_duplicates(subset=["folio"])
    hv = hv.merge(folio_state, on="folio", how="left").dropna(subset=["ent"])

    # Compute average debt by state
    hv["ent"] = hv["ent"].astype("Int64")
    state_avg = (
        hv.groupby("ent", as_index=False)["crh04_2"]
        .mean()
        .rename(columns={"ent": "state_code", "crh04_2": "avg_total_debt"})
    )

    # Filter states where average exceeds overall average
    state_avg = state_avg[state_avg["avg_total_debt"] > overall_avg]

    # Map state codes to names (based on provided metadata)
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
    state_avg["state_name"] = state_avg["state_code"].map(state_map)

    # Top 10 states by highest average debt
    result = state_avg.sort_values("avg_total_debt", ascending=False).head(10).reset_index(drop=True)

    return result[["state_code", "state_name", "avg_total_debt"]]