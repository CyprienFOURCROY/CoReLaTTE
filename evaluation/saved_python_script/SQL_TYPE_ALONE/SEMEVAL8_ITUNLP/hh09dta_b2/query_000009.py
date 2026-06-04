import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]]
    df_su = tables["ii_su"][["folio", "su01"]]
    df_se = tables["ii_se"][["folio", "se01e"]]

    # Households that use a plot of land for farming
    su_yes = df_su[df_su["su01"] == 1.0]
    # Households that reported a total crop loss in the last five years
    se_loss = df_se[df_se["se01e"] == 1.0]

    # Households satisfying both conditions
    hh = pd.merge(su_yes[["folio"]], se_loss[["folio"]], on="folio", how="inner")

    # Individuals in those households
    people = pd.merge(df_portad, hh, on="folio", how="inner")

    # Aggregate by state
    res = (
        people.groupby("ent", dropna=False)
        .agg(avg_age=("edad", "mean"), n_individuals=("edad", "size"))
        .reset_index()
    )

    # Map state codes to names
    state_map = {
        2.0: "Baja California",
        3.0: "Baja California Sur",
        4.0: "Campeche",
        5.0: "Coahuila",
        6.0: "Colima",
        7.0: "Chiapas",
        9.0: "Distrito Federal",
        10.0: "Durango",
        11.0: "Guanajuato",
        12.0: "Guerrero",
        13.0: "Hidalgo",
        14.0: "Jalisco",
        15.0: "Estado de México",
        16.0: "Michoacán",
        17.0: "Morelos",
        18.0: "Nayarit",
        19.0: "Nuevo León",
        20.0: "Oaxaca",
        21.0: "Puebla",
        22.0: "Querétaro",
        25.0: "Sinaloa",
        26.0: "Sonora",
        28.0: "Tamaulipas",
        29.0: "Tlaxcala",
        30.0: "Veracruz",
        31.0: "Yucatán",
        32.0: "Zacatecas",
    }
    res["state"] = res["ent"].map(state_map)

    res = res.sort_values("avg_age", ascending=False).reset_index(drop=True)
    res = res[["ent", "state", "avg_age", "n_individuals"]]
    return res