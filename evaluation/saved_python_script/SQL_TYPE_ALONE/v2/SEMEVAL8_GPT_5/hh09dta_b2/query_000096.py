import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Households with no savings
    no_savings_folios = set(df_crh.loc[df_crh["crh01_1a"] == 1.0, "folio"].dropna().astype(str).unique())

    # Households not using plot/land for farming
    no_land_folios = set(df_su.loc[df_su["su01"] == 3.0, "folio"].dropna().astype(str).unique())

    # Intersection: households satisfying both conditions
    target_folios = no_savings_folios & no_land_folios
    if not target_folios:
        return pd.DataFrame({"state": [], "households": []})

    # Get one state (ent) per household
    ent_by_folio = (
        df_portad[["folio", "ent"]]
        .dropna(subset=["ent"])
        .assign(folio=lambda x: x["folio"].astype(str))
        .groupby("folio", as_index=False)["ent"].first()
    )

    # Keep only target households
    ent_by_folio = ent_by_folio[ent_by_folio["folio"].isin(target_folios)].copy()
    if ent_by_folio.empty:
        return pd.DataFrame({"state": [], "households": []})

    ent_by_folio["ent"] = ent_by_folio["ent"].astype("Int64")

    # Count households per state
    counts = (
        ent_by_folio.groupby("ent", as_index=False)
        .agg(households=("folio", "nunique"))
    )

    # Filter states with at least 50 households
    counts = counts[counts["households"] >= 50].copy()
    if counts.empty:
        return pd.DataFrame({"state": [], "households": []})

    # Map state codes to names
    ent_to_name = {
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
        xi = int(x)
        return ent_to_name.get(xi, str(xi))

    counts["state"] = counts["ent"].apply(map_state)

    # Prepare final DataFrame
    result = counts.sort_values("households", ascending=False)[["state", "households"]].reset_index(drop=True)
    return result