def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]

    # Adults only
    df_adults = df_portad[df_portad["edad"] >= 18].copy()

    # Merge with vlh for "feel unsafe or very unsafe at home" (vlh04: 3 or 4)
    df_vlh_sel = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]
    df1 = df_adults.merge(df_vlh_sel[["folio", "vlh04", "vlh18a"]], on="folio", how="inner")

    # Merge with in for Liconsa milk (in03a == 1)
    df_in_liconsa = df_in[df_in["in03a"] == 1.0]
    df1 = df1.merge(df_in_liconsa[["folio", "in03a", "in02a10"]], on="folio", how="inner")

    # Only households with positive amount from Other Government Program (in02a10 > 0)
    df1 = df1[df1["in02a10"].notna() & (df1["in02a10"] > 0)]

    # Only households with vlh18a (total break-ins since 2005) above overall average
    overall_avg_breakins = df_vlh["vlh18a"].mean(skipna=True)
    df1 = df1[df1["vlh18a"].notna() & (df1["vlh18a"] > overall_avg_breakins)]

    # Group by state (ent), aggregate average age and count of adults
    result = (
        df1.groupby("ent")
        .agg(
            average_age=("edad", "mean"),
            num_adults=("folio", "count")
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
        32: "Zacatecas"
    }
    result["state"] = result["ent"].map(state_map)
    result = result.drop(columns="ent")
    result = result[["state", "average_age", "num_adults"]]
    result = result.sort_values("average_age", ascending=False).reset_index(drop=True)
    return result