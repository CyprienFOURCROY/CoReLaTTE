import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_vlh = tables["ii_vlh"]

    # Households that use a plot/land for farming (su01 == 1)
    su_yes = df_su.loc[df_su["su01"] == 1.0, ["folio"]].dropna().drop_duplicates()

    # Valid 'feel safe at home' responses
    vlh_valid = df_vlh.loc[~df_vlh["vlh04"].isna(), ["folio", "vlh04"]]

    # Merge to get households with both conditions
    hh = su_yes.merge(vlh_valid, on="folio", how="inner")

    # Map households to state (ent)
    ent_map = (
        df_portad.loc[~df_portad["ent"].isna(), ["folio", "ent"]]
        .drop_duplicates(subset=["folio"], keep="first")
    )
    hh = hh.merge(ent_map, on="folio", how="inner")

    # Group by state and compute average vlh04 and count of households
    grouped = hh.groupby("ent").agg(
        avg_vlh04=("vlh04", "mean"),
        households=("folio", "nunique"),
    ).reset_index()

    # Keep states with at least two households
    grouped = grouped[grouped["households"] >= 2]

    # Sort by lowest average vlh04 and take five states
    grouped = grouped.sort_values(by=["avg_vlh04", "ent"]).head(5)

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

    grouped["ent"] = grouped["ent"].astype("Int64")
    grouped["state"] = grouped["ent"].map(state_map).fillna("Unknown")

    # Reorder columns
    result = grouped[["ent", "state", "avg_vlh04", "households"]].reset_index(drop=True)
    return result