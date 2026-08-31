import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()

    # One state per household
    df_ent = df_portad.drop_duplicates(subset=["folio"])

    # Merge and filter households that use plot/land and have valid safety score and state
    df = (
        df_su.merge(df_vlh, on="folio", how="inner")
        .merge(df_ent, on="folio", how="left")
    )
    df = df[(df["su01"] == 1.0) & df["vlh04"].notna() & df["ent"].notna()]

    # Aggregate by state, requiring at least two households
    agg = (
        df.groupby("ent", as_index=False)
        .agg(avg_vlh04=("vlh04", "mean"), n_households=("vlh04", "size"))
    )
    agg = agg[agg["n_households"] >= 2].copy()

    # Sort to get five states with lowest average score
    agg = agg.sort_values(["avg_vlh04", "ent"], ascending=[True, True]).head(5).copy()

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
    agg["ent"] = agg["ent"].astype(int)
    agg["state"] = agg["ent"].map(state_map)

    return agg[["ent", "state", "avg_vlh04", "n_households"]]