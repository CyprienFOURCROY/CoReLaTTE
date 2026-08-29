import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]

    # Households with recorded total debt + interests value
    df_crh_val = df_crh[
        (df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna())
    ][["folio", "crh04_2"]].dropna(subset=["folio", "crh04_2"]).drop_duplicates(subset=["folio"])

    # Household to state mapping from roster (assume one state per household)
    df_ent = df_portad[["folio", "ent"]].dropna(subset=["folio", "ent"]).drop_duplicates(subset=["folio"])

    # Merge to attach state
    df = pd.merge(df_crh_val, df_ent, on="folio", how="left").dropna(subset=["ent"])

    # Overall average across all households with recorded value
    overall_avg = df["crh04_2"].mean()

    # Per-state averages and counts (households)
    grouped = df.groupby("ent", as_index=False).agg(
        average_amount=("crh04_2", "mean"),
        num_households=("folio", "nunique")
    )

    # Keep states with average > overall average
    grouped = grouped[grouped["average_amount"] > overall_avg].copy()

    # Map state codes to names
    ent_map = {
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

    def map_state(v):
        try:
            iv = int(v)
        except Exception:
            return None
        return ent_map.get(iv, str(iv))

    grouped["state"] = grouped["ent"].apply(map_state)

    result = grouped.sort_values("average_amount", ascending=False)[
        ["state", "average_amount", "num_households"]
    ].reset_index(drop=True)

    return result