import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()

    # Keep only adults (18+), then reduce to one row per household with state
    adults = df_portad[df_portad["edad"] >= 18]
    hh_ent = adults.groupby("folio", as_index=False)["ent"].first()

    # Collapse su and crh to household-level
    su_hh = df_su.groupby("folio", as_index=False).first()
    crh_hh = df_crh.groupby("folio", as_index=False).first()

    # Merge to household-level dataset
    hh = hh_ent.merge(su_hh, on="folio", how="inner").merge(crh_hh, on="folio", how="inner")

    # Filter: households that use land for farming and have positive total debt incl. interest
    mask = (hh["su01"] == 1.0) & (hh["crh04_2"] > 0)
    hh_filt = hh.loc[mask].copy()

    if hh_filt.empty:
        return pd.DataFrame(columns=["state_code", "state", "average_debt_pesos", "households"])

    # Aggregate by state
    agg = (
        hh_filt.groupby("ent", as_index=False)
        .agg(average_debt_pesos=("crh04_2", "mean"), households=("folio", "nunique"))
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
        32: "Zacatecas",
    }

    agg["state_code"] = agg["ent"].astype("int64")
    agg["state"] = agg["state_code"].map(state_map)

    # Sort by highest average debt and take top 10
    top10 = agg.sort_values("average_debt_pesos", ascending=False).head(10)

    # Select and order columns
    result = top10[["state_code", "state", "average_debt_pesos", "households"]].reset_index(drop=True)
    return result