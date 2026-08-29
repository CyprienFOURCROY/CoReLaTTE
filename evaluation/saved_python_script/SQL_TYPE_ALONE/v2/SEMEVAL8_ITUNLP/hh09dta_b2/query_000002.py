import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()

    # Compute overall average age among individuals with non-missing age
    avg_age = df_portad["edad"].mean()

    # Individuals older than overall average age
    df_older = df_portad[df_portad["edad"] > avg_age].copy()

    # Merge with household debts
    df_m = df_older.merge(
        df_crh[["folio", "crh04_1", "crh04_2"]],
        on="folio",
        how="left"
    )

    # Keep households that reported a positive debt amount with a valid value
    df_m = df_m[(df_m["crh04_1"] == 1.0) & (df_m["crh04_2"].notna()) & (df_m["crh04_2"] > 0)]

    if df_m.empty:
        return pd.DataFrame(columns=["state", "avg_household_total_debts_plus_interests_pesos", "num_individuals"])

    # Aggregate by state
    agg = (
        df_m.groupby("ent", dropna=False)
        .agg(
            avg_household_total_debts_plus_interests_pesos=("crh04_2", "mean"),
            num_individuals=("ls", "count"),
        )
        .reset_index()
    )

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
    agg["ent_code"] = agg["ent"].astype("Int64")
    agg["state"] = agg["ent_code"].map(state_map)

    # Sort and select top 5 states by average debt
    top5 = agg.sort_values("avg_household_total_debts_plus_interests_pesos", ascending=False).head(5)

    return top5[["state", "avg_household_total_debts_plus_interests_pesos", "num_individuals"]]