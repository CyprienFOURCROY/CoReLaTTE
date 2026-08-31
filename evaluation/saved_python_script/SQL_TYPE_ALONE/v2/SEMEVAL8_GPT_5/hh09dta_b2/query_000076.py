import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"].copy()
    df_vlh = tables["ii_vlh"].copy()
    df_portad = tables["ii_portad"].copy()

    # Households that report using a plot/land
    su_users = df_su.loc[df_su["su01"] == 1.0, ["folio"]].drop_duplicates()

    # Feel safe at home responses (valid: 1-4)
    df_vlh_sub = df_vlh[["folio", "vlh04"]].dropna(subset=["vlh04"])
    df_vlh_sub = df_vlh_sub[df_vlh_sub["vlh04"].isin([1.0, 2.0, 3.0, 4.0])].drop_duplicates(subset=["folio"])

    # State per household
    df_ent = df_portad[["folio", "ent"]].dropna(subset=["ent"]).drop_duplicates(subset=["folio"])

    # Merge to get households with plot usage, safety rating, and state
    merged = su_users.merge(df_vlh_sub, on="folio", how="inner").merge(df_ent, on="folio", how="left")
    merged = merged.dropna(subset=["ent"])

    # Group by state
    result = (
        merged.groupby("ent")
        .agg(avg_feel_safe=("vlh04", "mean"), n_households=("folio", "nunique"))
        .reset_index()
    )

    # Keep states with at least 30 such households
    result = result[result["n_households"] >= 30].copy()

    # State code to name mapping (from provided metadata)
    ent_map = {
        2.0: "Baja California",
        3.0: "Baja California Sur",
        4.0: "Campeche",
        5.0: "Coahuila",
        6.0: "Colima",
        7.0: "Chiapas",
        9.0: "Distrito Federal",
        10.0: "Durango",
        11.0: "Guanajuato",
        12.0: "Guerrero",
        13.0: "Hidalgo",
        14.0: "Jalisco",
        15.0: "Estado de México",
        16.0: "Michoacán",
        17.0: "Morelos",
        18.0: "Nayarit",
        19.0: "Nuevo León",
        20.0: "Oaxaca",
        21.0: "Puebla",
        22.0: "Querétaro",
        25.0: "Sinaloa",
        26.0: "Sonora",
        28.0: "Tamaulipas",
        29.0: "Tlaxcala",
        30.0: "Veracruz",
        31.0: "Yucatán",
        32.0: "Zacatecas",
    }
    result["state_name"] = result["ent"].map(ent_map).fillna("Unknown")

    # Ranking from safest (lowest average) to least safe
    result["rank"] = result["avg_feel_safe"].rank(method="dense", ascending=True).astype(int)

    # Prepare final output
    result = result.rename(columns={"ent": "state_code"})
    result = result[["state_code", "state_name", "n_households", "avg_feel_safe", "rank"]]
    result = result.sort_values(by=["avg_feel_safe", "state_code"]).reset_index(drop=True)

    return result