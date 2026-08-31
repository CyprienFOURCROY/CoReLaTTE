import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_se = tables["ii_se"][["folio", "se01b"]].copy()

    # Standardize folio as string and drop duplicates
    for df in (df_portad, df_vlh, df_se):
        df["folio"] = df["folio"].astype(str)
        df.dropna(subset=["folio"], inplace=True)
        df.drop_duplicates(subset=["folio"], inplace=True)

    # Conditions:
    # - Feel unsafe or very unsafe at home: vlh04 in {3, 4}
    # - Had illness/accident/hospitalization in last 5 years: se01b == 1
    unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]]
    illness = df_se[df_se["se01b"] == 1.0][["folio"]]

    # Households meeting both conditions
    hh_both = pd.merge(unsafe, illness, on="folio", how="inner").drop_duplicates(subset=["folio"])

    # Attach state
    hh_state = pd.merge(hh_both, df_portad[["folio", "ent"]], on="folio", how="left")
    hh_state = hh_state.dropna(subset=["ent"])
    hh_state["ent"] = hh_state["ent"].astype("Int64")

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
    hh_state["state"] = hh_state["ent"].map(state_map)
    hh_state = hh_state.dropna(subset=["state"])

    # Count unique households per state
    result = (
        hh_state.groupby("state")["folio"]
        .nunique()
        .reset_index(name="households")
    )

    # Filter states with at least 50 such households
    result = result[result["households"] >= 50].sort_values(by="households", ascending=False).reset_index(drop=True)

    return result