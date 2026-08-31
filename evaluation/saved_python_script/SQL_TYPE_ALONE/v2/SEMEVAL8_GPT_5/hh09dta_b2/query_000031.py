import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_vlh = tables["ii_vlh"].copy()
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()

    # Compute total incidents since 2005 per household
    counts = df_vlh[["vlh13a", "vlh15a", "vlh17a"]].fillna(0)
    df_vlh["incidents_since2005"] = df_vlh["vlh18a"]
    df_vlh["incidents_since2005"] = df_vlh["incidents_since2005"].where(
        df_vlh["incidents_since2005"].notna(),
        counts.sum(axis=1)
    ).fillna(0)

    hh_inc = df_vlh.loc[df_vlh["incidents_since2005"] > 0, ["folio", "incidents_since2005"]].dropna(subset=["folio"])

    # One state per household
    df_portad = df_portad.dropna(subset=["folio"]).drop_duplicates(subset=["folio"], keep="first")

    merged = hh_inc.merge(df_portad, on="folio", how="left")

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
    ent_int = pd.to_numeric(merged["ent"], errors="coerce").astype("Int64")
    merged["state"] = ent_int.map(state_map)
    merged = merged.dropna(subset=["state"])

    grouped = merged.groupby("state", as_index=False).agg(
        households_with_incidents=("folio", "nunique"),
        total_incidents=("incidents_since2005", "sum"),
    )

    # Average across states with any incidents (all in grouped have incidents)
    avg_total = grouped["total_incidents"].mean()

    result = grouped[
        (grouped["households_with_incidents"] >= 100) & (grouped["total_incidents"] > avg_total)
    ].sort_values(by="total_incidents", ascending=False)

    return result.reset_index(drop=True)