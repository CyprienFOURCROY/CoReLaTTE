import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_se = tables["ii_se"]

    # Households that own an electronic device
    ed_folios = pd.Series(df_ah.loc[df_ah["ah03e"] == 1.0, "folio"].dropna().unique())

    # Households that reported losing dwelling/business to a natural disaster in last 5 years
    nd_folios = pd.Series(df_se.loc[df_se["se01d"] == 1.0, "folio"].dropna().unique())

    # Intersection of households satisfying both conditions
    common_folios = set(ed_folios.tolist()).intersection(set(nd_folios.tolist()))

    # Filter individuals from those households
    df_filtered = df_portad[df_portad["folio"].isin(common_folios)].copy()

    if df_filtered.empty:
        return pd.DataFrame(columns=["state_code", "state", "average_age", "individuals"])

    # Group by state and compute average age and count of individuals (non-null age)
    result = (
        df_filtered.groupby("ent", as_index=False)
        .agg(
            average_age=("edad", "mean"),
            individuals=("edad", lambda s: s.notna().sum()),
        )
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
    result["state_code"] = result["ent"].astype("Int64")
    result["state"] = result["state_code"].map(state_map)

    # Order by highest average age
    result = result.sort_values(by="average_age", ascending=False)

    # Final columns order
    result = result[["state_code", "state", "average_age", "individuals"]].reset_index(drop=True)

    return result