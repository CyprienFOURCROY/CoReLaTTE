def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_in = tables["ii_in"]

    # Households with at least one member who owns an electronic device (ah03e == 1)
    owns_electronic = df_ah[df_ah["ah03e"] == 1.0][["folio"]].drop_duplicates()

    # Households with positive amount received from "Other Government Program"
    # in01a10_2: amount received
    # in01a10_1: 1 means received income
    df_in_pos = df_in[(df_in["in01a10_1"] == 1.0) & (df_in["in01a10_2"] > 0)]

    # Merge to keep only households that satisfy both conditions
    eligible = df_in_pos.merge(owns_electronic, on="folio", how="inner")

    # Merge with df_portad to get state info (ent)
    eligible = eligible.merge(df_portad[["folio", "ent"]].drop_duplicates(), on="folio", how="left")

    # Group by state, aggregate
    result = (
        eligible.groupby("ent")
        .agg(
            n_households=("folio", "nunique"),
            avg_amount=("in01a10_2", "mean")
        )
        .reset_index()
    )

    # Filter: at least 30 households and average > 2000
    result = result[(result["n_households"] >= 30) & (result["avg_amount"] > 2000)]

    # Order from highest to lowest average
    result = result.sort_values("avg_amount", ascending=False)

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
    result = result[["state", "n_households", "avg_amount"]].reset_index(drop=True)
    return result