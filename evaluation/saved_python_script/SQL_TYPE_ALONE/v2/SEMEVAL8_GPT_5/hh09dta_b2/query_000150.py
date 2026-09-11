import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()

    # Merge datasets on folio (household ID)
    df = df_portad.merge(df_vlh, on="folio", how="inner").merge(df_crh, on="folio", how="inner")

    # Determine households with reported total debt (including interests)
    reported_mask = (df["crh04_1"] == 1.0) & (df["crh04_2"].notna())

    # National average across all households with reported debt values
    national_df = df.loc[reported_mask, ["folio", "crh04_2"]].copy()
    if national_df.empty:
        return pd.DataFrame(columns=["ent", "state", "avg_total_debt", "avg_age", "n_households"])
    national_avg = national_df["crh04_2"].mean()

    # Filter to households who feel unsafe or very unsafe at home and have reported debt values
    unsafe_mask = df["vlh04"].isin([3.0, 4.0])
    target_df = df.loc[reported_mask & unsafe_mask].copy()
    if target_df.empty:
        return pd.DataFrame(columns=["ent", "state", "avg_total_debt", "avg_age", "n_households"])

    # Ensure state codes are integer-like for grouping and mapping
    target_df["ent"] = target_df["ent"].astype("Int64")

    # Group by state
    grouped = (
        target_df.groupby("ent", dropna=True)
        .agg(
            avg_total_debt=("crh04_2", "mean"),
            avg_age=("edad", "mean"),
            n_households=("folio", "nunique"),
        )
        .reset_index()
    )

    # Filter states exceeding national average
    result = grouped[grouped["avg_total_debt"] > national_avg].copy()

    # Map state codes to names
    states_map = {
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
    result["state"] = result["ent"].map(states_map)

    # Order from highest to lowest average debt
    result = result.sort_values(by="avg_total_debt", ascending=False)

    # Final columns and types
    result["ent"] = result["ent"].astype("Int64")
    result = result[["ent", "state", "avg_total_debt", "avg_age", "n_households"]].reset_index(drop=True)

    return result