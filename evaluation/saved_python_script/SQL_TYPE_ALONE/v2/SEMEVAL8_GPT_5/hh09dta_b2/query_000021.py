import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh10a"]].copy()

    # Ensure one row per household from portad
    df_portad = df_portad.drop_duplicates(subset=["folio"])
    # Drop missing state codes
    df_portad = df_portad[~df_portad["ent"].isna()].copy()

    # Merge to attach state to household victimization info
    df = pd.merge(df_portad, df_vlh, on="folio", how="inner")

    # Prepare state code as integer
    df["ent"] = df["ent"].astype("Int64")

    # Aggregate per state
    agg = (
        df.groupby("ent", as_index=False)
        .agg(
            total_households=("folio", "nunique"),
            households_knowing_robbery_12m=("vlh10a", lambda s: (s == 1.0).sum()),
        )
    )

    # Filter states with at least 100 surveyed households
    agg = agg[agg["total_households"] >= 100].copy()

    # Map state names (optional for readability)
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
    agg["state"] = agg["ent"].map(state_map)

    # Sort ranking from highest to lowest by count of households knowing a robbery
    agg = agg.sort_values(
        by=["households_knowing_robbery_12m", "total_households", "ent"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    # Ensure integer dtypes
    agg["total_households"] = agg["total_households"].astype("Int64")
    agg["households_knowing_robbery_12m"] = agg["households_knowing_robbery_12m"].astype("Int64")

    # Reorder columns
    agg = agg[["ent", "state", "households_knowing_robbery_12m", "total_households"]]

    return agg