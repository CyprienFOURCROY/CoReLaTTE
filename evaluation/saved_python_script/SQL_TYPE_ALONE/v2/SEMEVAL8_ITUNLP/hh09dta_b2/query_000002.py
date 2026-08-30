import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()

    # Compute overall average age
    avg_age = df_portad["edad"].mean(skipna=True)

    # Filter interviewed individuals older than overall average age
    df_older = df_portad[df_portad["edad"] > avg_age][["folio", "ent"]].copy()

    # Merge with household debts
    df_crh_sub = df_crh[["folio", "crh04_2"]].copy()
    df = df_older.merge(df_crh_sub, on="folio", how="inner")

    # Keep only positive reported debt amounts
    df = df[df["crh04_2"].notna() & (df["crh04_2"] > 0)]

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

    # Count individuals per state (among filtered)
    ind_counts = (
        df.groupby("ent", dropna=False)
        .size()
        .reset_index(name="n_individuals")
    )

    # Compute average household debt per state using unique households
    households = df.drop_duplicates(subset=["folio"])[["folio", "ent", "crh04_2"]]
    avg_debt_by_ent = (
        households.groupby("ent", dropna=False)["crh04_2"]
        .mean()
        .reset_index(name="avg_debt")
    )

    # Merge results
    res = avg_debt_by_ent.merge(ind_counts, on="ent", how="inner")

    # Add state names and filter valid states
    res["ent_int"] = res["ent"].astype("Int64")
    res["state"] = res["ent_int"].map(state_map)
    res = res[res["state"].notna()]

    # Get top five states by average debt
    res = res.sort_values(by="avg_debt", ascending=False).head(5)

    return res[["state", "avg_debt", "n_individuals"]].reset_index(drop=True)