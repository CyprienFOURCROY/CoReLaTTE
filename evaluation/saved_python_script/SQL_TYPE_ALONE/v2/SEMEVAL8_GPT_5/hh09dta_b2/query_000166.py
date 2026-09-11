import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].drop_duplicates(subset=["folio"]).copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04", "vlh10a"]].drop_duplicates(subset=["folio"]).copy()

    # Filter households who answered 'No' (3) to knowing a family/friend robbed in last 12 months
    df_vlh = df_vlh[(df_vlh["vlh10a"] == 3) & (df_vlh["vlh04"].notna())]

    # Join to get state
    df = df_vlh.merge(df_portad, on="folio", how="left")
    df = df[df["ent"].notna()].copy()
    if df.empty:
        return pd.DataFrame(columns=["state", "avg_feel_safe_at_home", "households"])

    # Compute national average for this group
    nat_avg = df["vlh04"].mean()

    # Group by state
    grp = (
        df.groupby(df["ent"].astype("Int64"))
        .agg(avg_feel_safe_at_home=("vlh04", "mean"), households=("folio", "size"))
        .reset_index()
        .rename(columns={"ent": "ent_code"})
    )

    # Filter states with average >= 3 and above national average
    grp = grp[(grp["avg_feel_safe_at_home"] >= 3) & (grp["avg_feel_safe_at_home"] > nat_avg)]

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
    if grp.empty:
        return pd.DataFrame(columns=["state", "avg_feel_safe_at_home", "households"])

    grp["state"] = grp["ent_code"].astype("Int64").map(ent_map).astype(str)

    # Sort from highest average (least safe) to lowest; tie-break by households desc then state asc
    grp = grp.sort_values(by=["avg_feel_safe_at_home", "households", "state"], ascending=[False, False, True])

    # Select and return
    result = grp[["state", "avg_feel_safe_at_home", "households"]].reset_index(drop=True)
    return result