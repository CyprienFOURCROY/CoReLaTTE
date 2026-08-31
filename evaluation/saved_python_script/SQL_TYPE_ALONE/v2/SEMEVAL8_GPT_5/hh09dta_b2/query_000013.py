import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()
    df_su = tables["ii_su"].copy()

    # Household conditions
    folios_bars = set(df_vlh.loc[df_vlh["vlh07b"] == 1, "folio"].dropna().unique())
    folios_plot = set(df_su.loc[df_su["su01"] == 1, "folio"].dropna().unique())
    eligible_folios = folios_bars.intersection(folios_plot)

    # Adults 18+ in eligible households
    adults = df_portad.loc[
        (df_portad["edad"].notna()) & (df_portad["edad"] >= 18) & (df_portad["folio"].isin(eligible_folios))
    ].copy()

    if adults.empty:
        return pd.DataFrame(columns=["state", "average_age", "n_adults"])

    # Group by state
    grp = (
        adults.groupby("ent", dropna=False)
        .agg(average_age=("edad", "mean"), n_adults=("edad", "size"))
        .reset_index()
    )

    # Map state codes to names (from metadata)
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

    # Ensure integer-like for mapping
    grp["ent_int"] = grp["ent"].astype("Int64")
    grp["state"] = grp["ent_int"].map(state_map).astype("object")
    grp["state"] = grp["state"].fillna(grp["ent_int"].astype(str))

    # Sort by highest average age, break ties by larger n_adults, then state name
    grp_sorted = grp.sort_values(by=["average_age", "n_adults", "state"], ascending=[False, False, True])

    result = grp_sorted.head(5)[["state", "average_age", "n_adults"]].reset_index(drop=True)
    return result