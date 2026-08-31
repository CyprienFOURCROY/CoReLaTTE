import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_in = tables["ii_in"][["folio", "in03a"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_ah = tables["ii_ah"][["folio", "ah04e_2"]].copy()

    # Deduplicate to one row per household
    df_portad = df_portad.dropna(subset=["folio"]).groupby("folio", as_index=False).first()
    df_ah = df_ah.dropna(subset=["folio"]).groupby("folio", as_index=False).first()
    df_in = df_in.dropna(subset=["folio"]).groupby("folio", as_index=False).first()
    df_vlh = df_vlh.dropna(subset=["folio"]).groupby("folio", as_index=False).first()

    # Filter criteria
    in_yes = df_in[df_in["in03a"] == 1.0][["folio"]]
    vlh_safe = df_vlh[df_vlh["vlh04"].isin([1.0, 2.0])][["folio"]]

    eligible = pd.merge(in_yes, vlh_safe, on="folio", how="inner")

    # Merge with assets and state
    merged = eligible.merge(df_ah, on="folio", how="left").merge(df_portad, on="folio", how="left")

    # Ensure ent present and compute value
    merged = merged.dropna(subset=["ent"])
    merged["val"] = merged["ah04e_2"].fillna(0)

    if merged.empty:
        return pd.DataFrame(columns=["state", "avg_value_electronic_devices"])

    overall_avg = merged["val"].mean()

    state_avg = (
        merged.groupby("ent", as_index=False)["val"]
        .mean()
        .rename(columns={"val": "avg_value_electronic_devices"})
    )

    # Filter states above overall average
    state_above = state_avg[state_avg["avg_value_electronic_devices"] > overall_avg].copy()

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

    def code_to_name(x):
        try:
            xi = int(x)
            return state_map.get(xi, str(xi))
        except Exception:
            return str(x)

    state_above["state"] = state_above["ent"].apply(code_to_name)

    result = state_above.sort_values(
        by="avg_value_electronic_devices", ascending=False
    )[["state", "avg_value_electronic_devices"]].reset_index(drop=True)

    return result