def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]

    # 1. Compute overall average age (excluding NaN)
    avg_age = df_portad["edad"].mean()

    # 2. Filter individuals older than average age
    df_portad_older = df_portad[df_portad["edad"] > avg_age]

    # 3. Merge with crh to get debts info
    df_merged = df_portad_older.merge(df_crh[["folio", "crh04_2"]], on="folio", how="left")

    # 4. Only households that reported a positive debt amount
    df_positive_debt = df_merged[df_merged["crh04_2"].notna() & (df_merged["crh04_2"] > 0)]

    # 5. Group by state, calculate average debt and count
    state_avg = (
        df_positive_debt
        .groupby("ent")
        .agg(
            avg_debt=("crh04_2", "mean"),
            n_individuals=("folio", "count")
        )
        .reset_index()
    )

    # 6. Map state codes to names
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
        32: "Zacatecas"
    }
    state_avg["state"] = state_avg["ent"].map(state_map)

    # 7. Sort by avg_debt descending, take top 5
    top5 = state_avg.sort_values("avg_debt", ascending=False).head(5)

    # 8. Select and reorder columns
    result = top5[["state", "avg_debt", "n_individuals"]].reset_index(drop=True)

    return result