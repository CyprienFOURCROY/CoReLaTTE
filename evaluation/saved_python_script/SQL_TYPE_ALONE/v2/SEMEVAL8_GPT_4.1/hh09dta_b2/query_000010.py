def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_se = tables["ii_se"]

    # Households that experienced disease/accident/hospitalization in last 5 years
    # se01b == 1 means Yes
    hh_disease = df_se[df_se["se01b"] == 1.0][["folio"]].drop_duplicates()

    # Merge with asset table to get value of electronic devices
    df_ah_hh = df_ah.merge(hh_disease, on="folio", how="inner")

    # Only keep households where value of electronic device is present and positive
    # ah04e_2 is the value, ah04e_1==1 means value is reported
    df_ah_hh = df_ah_hh[(df_ah_hh["ah04e_1"] == 1.0) & (df_ah_hh["ah04e_2"].notna()) & (df_ah_hh["ah04e_2"] > 0)]

    # Merge with portad to get state
    df_ah_hh = df_ah_hh.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Group by state, compute average and count of households (unique folio)
    grouped = (
        df_ah_hh.groupby("ent")
        .agg(
            avg_value_electronic_device=("ah04e_2", "mean"),
            n_households=("folio", "nunique")
        )
        .reset_index()
    )

    # Only states with at least 2 such households
    grouped = grouped[grouped["n_households"] >= 2]

    # Sort by average value descending, take top 10
    grouped = grouped.sort_values("avg_value_electronic_device", ascending=False).head(10)

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
    grouped["state"] = grouped["ent"].map(state_map)

    # Reorder columns
    result = grouped[["state", "avg_value_electronic_device", "n_households"]].reset_index(drop=True)
    return result