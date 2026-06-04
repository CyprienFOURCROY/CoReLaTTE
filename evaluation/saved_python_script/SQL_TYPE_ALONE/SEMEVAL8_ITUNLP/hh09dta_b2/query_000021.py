import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]

    # Individuals with ID '01' aged 30+
    head = df_portad.loc[(df_portad["ls"] == "01") & (df_portad["edad"] >= 30), ["folio", "ent"]].dropna(subset=["folio", "ent"]).drop_duplicates("folio")

    # Households that use land for farming
    su = df_su.loc[df_su["su01"] == 1.0, ["folio", "su234"]].dropna(subset=["folio"])

    # Households that own/share a non-ag business
    nna = df_nna.loc[df_nna["nna01"] == 1.0, ["folio"]].dropna(subset=["folio"]).drop_duplicates()

    # Merge filters
    hh = su.merge(nna, on="folio", how="inner").merge(head, on="folio", how="inner").dropna(subset=["su234"])
    if hh.empty:
        return pd.DataFrame({"ent": pd.Series(dtype="Int64"), "state": pd.Series(dtype="object"), "avg_seeds_spending": pd.Series(dtype="float64")})

    # Average spending on seeds by state
    state_avg = hh.groupby("ent", as_index=False)["su234"].mean()

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

    state_avg = state_avg.sort_values("su234", ascending=False).head(5)
    state_avg["ent"] = state_avg["ent"].astype("Int64")
    state_avg["state"] = state_avg["ent"].map(ent_to_state)
    state_avg = state_avg.rename(columns={"su234": "avg_seeds_spending"})
    return state_avg[["ent", "state", "avg_seeds_spending"]]