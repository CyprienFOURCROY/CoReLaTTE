def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_crh = tables["ii_crh"]

    # Merge all tables on 'folio'
    df = df_portad.merge(df_vlh, on="folio", how="inner").merge(df_crh, on="folio", how="inner")

    # Only consider households with a reported debt value (crh04_2 not null)
    df_debt = df[df["crh04_2"].notnull()].copy()

    # Compute national average total debt (including interests) among all with reported debt
    national_avg_debt = df_debt["crh04_2"].mean()

    # Households who feel unsafe or very unsafe at home (vlh04 == 3 or 4)
    mask_unsafe = df_debt["vlh04"].isin([3.0, 4.0])
    df_unsafe = df_debt[mask_unsafe].copy()

    # Group by state and compute required stats
    grouped = (
        df_unsafe.groupby("ent")
        .agg(
            avg_total_debt=("crh04_2", "mean"),
            avg_age=("edad", "mean"),
            n_households=("folio", "count")
        )
        .reset_index()
    )

    # Only keep states where avg_total_debt > national_avg_debt
    result = grouped[grouped["avg_total_debt"] > national_avg_debt].copy()

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
    result["state"] = result["ent"].map(state_map)

    # Order from highest to lowest average debt
    result = result.sort_values("avg_total_debt", ascending=False)

    # Select and reorder columns
    result = result[["state", "avg_total_debt", "avg_age", "n_households"]].reset_index(drop=True)

    return result