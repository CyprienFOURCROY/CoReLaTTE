import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_crh = tables["ii_crh"].copy()

    # Keep only necessary columns and ensure unique households
    p = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])
    a = df_ah[["folio", "ah03d"]].drop_duplicates(subset=["folio"])
    c = df_crh[["folio", "crh04_1", "crh04_2"]].drop_duplicates(subset=["folio"])

    # Merge datasets
    m = p.merge(a, on="folio", how="inner").merge(c, on="folio", how="inner")

    # Filter: owns motor vehicle and reported a value for total debts (including interest)
    mask = (m["ah03d"] == 1.0) & (m["crh04_1"] == 1.0) & (m["crh04_2"].notna())
    df = m.loc[mask, ["folio", "ent", "crh04_2"]].copy()

    if df.empty:
        return pd.DataFrame(columns=["ent", "state", "count_above_avg"])

    # Compute nationwide average debt among these households
    overall_avg = df["crh04_2"].mean()

    # Identify households with debt above the average
    df = df[df["crh04_2"] > overall_avg].copy()

    # Group by state and count
    res = df.groupby("ent", as_index=False).size().rename(columns={"size": "count_above_avg"})

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
    # Ensure integer dtype for mapping
    res["ent"] = res["ent"].astype("Int64")
    res["state"] = res["ent"].map(lambda x: state_map.get(int(x) if pd.notna(x) else x, None))

    # Sort to show states with the highest counts first
    res = res.sort_values(["count_above_avg", "ent"], ascending=[False, True]).reset_index(drop=True)

    return res