def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]

    # Households where a member owns a motor vehicle (ah03d == 1)
    df_ah_mv = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # Households where a resident reports feeling safe or very safe at home (vlh04 == 1 or 2)
    df_vlh_safe = df_vlh[df_vlh["vlh04"].isin([1.0, 2.0])][["folio"]].drop_duplicates()

    # Intersection: households with both conditions
    df_households = pd.merge(df_ah_mv, df_vlh_safe, on="folio", how="inner")

    # Add state info from ii_portad (one row per household)
    df_households = pd.merge(
        df_households,
        df_portad[["folio", "ent"]].drop_duplicates("folio"),
        on="folio",
        how="left"
    )

    # Count households per state
    result = (
        df_households.groupby("ent")
        .size()
        .reset_index(name="num_households")
    )

    # Filter states with at least 100 households
    result = result[result["num_households"] >= 100]

    # Sort by count descending
    result = result.sort_values("num_households", ascending=False).reset_index(drop=True)

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
    result = result[["state", "num_households"]]

    return result.reset_index(drop=True)