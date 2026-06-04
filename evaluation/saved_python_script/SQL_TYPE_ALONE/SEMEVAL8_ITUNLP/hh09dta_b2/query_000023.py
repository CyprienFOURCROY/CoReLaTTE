import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_su = tables["ii_su"]

    # Households using plot/land for farming
    su_yes_folios = set(df_su.loc[df_su["su01"] == 1.0, "folio"].dropna().unique())
    # Households owning/sharing a non-ag business
    nna_yes_folios = set(df_nna.loc[df_nna["nna01"] == 1.0, "folio"].dropna().unique())
    # Households satisfying both conditions
    eligible_folios = su_yes_folios & nna_yes_folios

    # Adults (18+) living in eligible households
    adults = df_portad.loc[(df_portad["edad"] >= 18) & (df_portad["folio"].isin(list(eligible_folios)))]

    if adults.empty:
        return pd.DataFrame({"ent": pd.Series(dtype="float64"),
                             "state": pd.Series(dtype="object"),
                             "adult_count": pd.Series(dtype="int64")})

    counts = adults.groupby("ent", dropna=False).size().reset_index(name="adult_count")

    # Get maximum count
    max_count = counts["adult_count"].max()
    top_states = counts.loc[counts["adult_count"] == max_count].copy()

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
    def map_state(x):
        if pd.isna(x):
            return None
        try:
            return state_map.get(int(x))
        except Exception:
            return None

    top_states["state"] = top_states["ent"].apply(map_state)

    # Reorder columns
    return top_states[["ent", "state", "adult_count"]]