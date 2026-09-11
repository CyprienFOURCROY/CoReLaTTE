import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["edad", "ent", "folio"]].copy()
    df_inr = tables["ii_inr"][["folio", "inr02c", "inr02d"]].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()

    # Households that use a plot/land for farming
    su_ok_hh = (
        df_su.loc[df_su["su01"] == 1, "folio"]
        .dropna()
        .astype(str)
        .unique()
    )

    # Households that produced/sold both meat and eggs in last 12 months
    df_inr["meat_yes"] = df_inr["inr02c"].eq(1)
    df_inr["eggs_yes"] = df_inr["inr02d"].eq(1)
    inr_agg = df_inr.groupby("folio")[["meat_yes", "eggs_yes"]].any().reset_index()
    inr_ok_hh = inr_agg.loc[inr_agg["meat_yes"] & inr_agg["eggs_yes"], "folio"].astype(str).values

    qualifying_hh = pd.Index(su_ok_hh).intersection(pd.Index(inr_ok_hh))

    persons = df_portad[df_portad["folio"].astype(str).isin(qualifying_hh)].copy()
    persons = persons.dropna(subset=["edad", "ent"])
    if persons.empty:
        return pd.DataFrame(columns=["state", "average_age", "n_individuals"])

    overall_avg = persons["edad"].mean()

    grp = (
        persons.groupby("ent")
        .agg(average_age=("edad", "mean"), n_individuals=("edad", "size"))
        .reset_index()
    )

    grp_filtered = grp[(grp["n_individuals"] >= 30) & (grp["average_age"] > overall_avg)].copy()

    mapping = {
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

    def map_state_code(x):
        try:
            code = int(round(float(x)))
        except Exception:
            return str(x)
        return mapping.get(code, str(code))

    grp_filtered["state"] = grp_filtered["ent"].apply(map_state_code)

    result = grp_filtered[["state", "average_age", "n_individuals"]].sort_values(
        by="average_age", ascending=False
    ).reset_index(drop=True)

    return result