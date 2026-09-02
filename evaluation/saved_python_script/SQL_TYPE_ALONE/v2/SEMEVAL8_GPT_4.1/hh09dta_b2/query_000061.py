def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_inr = tables["ii_inr"]

    # Households that use a plot/land for farming/vegetables (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Households that did NOT produce/sell honey in last 12 months (inr02i == 3)
    inr_no_honey = df_inr[df_inr["inr02i"] == 3][["folio"]].drop_duplicates()

    # Intersection: households that satisfy both conditions
    eligible_folios = pd.merge(su_plot, inr_no_honey, on="folio")

    # Merge with portad to get state and age
    merged = pd.merge(eligible_folios, df_portad, on="folio", how="inner")

    # Compute overall average age across all respondents
    overall_avg_age = df_portad["edad"].mean()

    # Group by state, count households, compute average age
    grouped = (
        merged.groupby("ent")
        .agg(
            num_households=("folio", "nunique"),
            avg_age=("edad", "mean")
        )
        .reset_index()
    )

    # Filter: at least 40 households and avg_age < overall_avg_age
    filtered = grouped[(grouped["num_households"] >= 40) & (grouped["avg_age"] < overall_avg_age)]

    # Order by avg_age ascending
    filtered = filtered.sort_values("avg_age", ascending=True)

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
        32: "Zacatecas"
    }
    filtered["state"] = filtered["ent"].map(state_map)

    # Reorder columns
    result = filtered[["state", "num_households", "avg_age"]].reset_index(drop=True)

    return result