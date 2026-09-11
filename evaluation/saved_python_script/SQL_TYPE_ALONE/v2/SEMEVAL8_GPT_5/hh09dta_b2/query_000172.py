import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]

    # Identify households that use land for farming
    su_folios = (
        df_su.loc[df_su["su01"] == 1.0, ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates()
    )

    # Identify households that produced/sold honey in last 12 months
    inr_folios = (
        df_inr.loc[df_inr["inr02i"] == 1.0, ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates()
    )

    # Households satisfying both conditions
    target_folios = su_folios.merge(inr_folios, on="folio", how="inner")

    # Join with individuals to get ages and state
    ppl = df_portad.merge(target_folios, on="folio", how="inner")[["ent", "edad"]]
    ppl = ppl.dropna(subset=["edad", "ent"])

    if ppl.empty:
        return pd.DataFrame(columns=["state", "average_age"])

    overall_avg = ppl["edad"].mean()

    by_state = (
        ppl.groupby("ent", as_index=False)["edad"]
        .mean()
        .rename(columns={"edad": "average_age"})
    )

    # Filter states with avg age greater than overall average
    by_state = by_state[by_state["average_age"] > overall_avg].copy()
    if by_state.empty:
        return pd.DataFrame(columns=["state", "average_age"])

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

    by_state["ent_int"] = by_state["ent"].astype("Int64")
    by_state["state"] = by_state["ent_int"].map(state_map).fillna(by_state["ent_int"].astype(str))

    result = by_state[["state", "average_age"]].sort_values("average_age", ascending=False).reset_index(drop=True)
    return result