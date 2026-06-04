import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()

    # Map households to state
    hh_state = (
        df_portad.loc[:, ["folio", "ent"]]
        .dropna(subset=["ent"])
        .drop_duplicates(subset=["folio"])
        .copy()
    )
    hh_state["ent"] = hh_state["ent"].astype("Int64")

    # Positive amounts from Other Government Program
    in_other = df_in.loc[:, ["folio", "in02a10"]].copy()
    in_other = in_other[in_other["in02a10"].notna() & (in_other["in02a10"] > 0)]

    # Merge and keep valid states
    merged = in_other.merge(hh_state, on="folio", how="left")
    merged = merged[merged["ent"].notna()].copy()

    if merged.empty:
        return pd.DataFrame({"state": [], "recipient_households": [], "avg_amount": []})

    summary = (
        merged.groupby("ent", dropna=True)
        .agg(avg_amount=("in02a10", "mean"), recipient_households=("folio", "nunique"))
        .reset_index()
    )

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

    summary["state"] = summary["ent"].astype("Int64").map(ent_map)
    summary["state"] = summary["state"].fillna(summary["ent"].astype("Int64").astype(str))

    idx = summary["avg_amount"].idxmax()
    result = summary.loc[[idx], ["state", "recipient_households", "avg_amount"]].reset_index(drop=True)
    return result