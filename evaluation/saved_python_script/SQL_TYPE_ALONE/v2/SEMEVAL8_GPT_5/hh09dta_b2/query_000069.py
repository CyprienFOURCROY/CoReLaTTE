import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["edad", "ent", "folio"]].copy()
    df_inr = tables["ii_inr"][["folio", "inr02f"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    # Filter conditions
    df_inr_crafts = df_inr[df_inr["inr02f"] == 1.0]
    df_vlh_safe = df_vlh[df_vlh["vlh04"].isin([1.0, 2.0])]

    # Merge to identify eligible respondents
    merged = df_portad.merge(df_inr_crafts, on="folio", how="inner").merge(df_vlh_safe, on="folio", how="inner")
    merged = merged[merged["edad"] >= 30]

    # Universe of states (all states present in the dataset)
    ent_universe = df_portad["ent"].dropna()
    if ent_universe.empty:
        return pd.DataFrame({"state": [], "respondent_count": []})
    ent_universe = pd.Index(pd.Series(ent_universe.astype("Int64")).unique())

    # Counts per state for eligible respondents
    merged["ent_int"] = merged["ent"].astype("Int64")
    counts = merged.groupby("ent_int").size()
    counts = counts.reindex(ent_universe, fill_value=0)

    # Average across states and selection
    avg_count = counts.mean()
    selected = counts[counts >= avg_count].sort_values(ascending=False)

    # Map state codes to names
    state_map = {
        1: "Aguascalientes",
        2: "Baja California",
        3: "Baja California Sur",
        4: "Campeche",
        5: "Coahuila",
        6: "Colima",
        7: "Chiapas",
        8: "Chihuahua",
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
        23: "Quintana Roo",
        24: "San Luis Potosí",
        25: "Sinaloa",
        26: "Sonora",
        27: "Tabasco",
        28: "Tamaulipas",
        29: "Tlaxcala",
        30: "Veracruz",
        31: "Yucatán",
        32: "Zacatecas",
    }

    res = selected.reset_index()
    res.columns = ["ent", "respondent_count"]
    res["state"] = res["ent"].astype("Int64").map(state_map)
    res["state"] = res["state"].fillna(res["ent"].astype("Int64").astype(str))
    res = res[["state", "respondent_count"]]

    return res