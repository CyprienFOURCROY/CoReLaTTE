import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_inr = tables["ii_inr"]

    # Households that feel unsafe or very unsafe at home
    hhs_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]].dropna().drop_duplicates()

    # Households that produced/sold crafts in the last 12 months
    hhs_crafts = df_inr[df_inr["inr02f"] == 1.0][["folio"]].dropna().drop_duplicates()

    # Households satisfying both conditions
    target_hhs = hhs_unsafe.merge(hhs_crafts, on="folio", how="inner")

    # Individuals living in those households
    people = df_portad.merge(target_hhs, on="folio", how="inner")

    # Compute average age by state (ent)
    people = people.dropna(subset=["edad", "ent"])
    if people.empty:
        return pd.DataFrame({"ent": pd.Series(dtype="int64"),
                             "state": pd.Series(dtype="object"),
                             "average_age": pd.Series(dtype="float64")})

    avg_by_ent = people.groupby("ent", as_index=False)["edad"].mean()

    if avg_by_ent.empty:
        return pd.DataFrame({"ent": pd.Series(dtype="int64"),
                             "state": pd.Series(dtype="object"),
                             "average_age": pd.Series(dtype="float64")})

    max_avg = avg_by_ent["edad"].max()
    top_states = avg_by_ent[avg_by_ent["edad"] == max_avg].copy()

    # Map state codes to names based on provided metadata
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

    top_states["ent"] = top_states["ent"].astype("int64")
    top_states["state"] = top_states["ent"].map(state_map).fillna("Unknown")
    top_states = top_states.rename(columns={"edad": "average_age"})
    return top_states[["ent", "state", "average_age"]]