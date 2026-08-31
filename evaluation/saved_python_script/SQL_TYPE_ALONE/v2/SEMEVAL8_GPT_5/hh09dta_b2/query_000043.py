import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()
    df_ah = tables["ii_ah"].copy()

    # Adults (18+)
    adults = df_portad[(df_portad["edad"].notna()) & (df_portad["edad"] >= 18)]

    # Households with no forced-entry robbery since 2005
    hh_no_rob = df_vlh[df_vlh["vlh12a_c"] == 3.0][["folio"]].drop_duplicates()

    # Households where at least one member owns a motor car
    has_car = (df_ah["ah03d1"] == 1.0).groupby(df_ah["folio"]).any().reset_index(name="has_car")
    hh_has_car = has_car[has_car["has_car"]][["folio"]]

    # Eligible households: both conditions
    hh_ok = hh_no_rob.merge(hh_has_car, on="folio", how="inner")

    # Adults living in eligible households
    adults_in_ok = adults.merge(hh_ok, on="folio", how="inner")

    # Count adults by state
    counts = adults_in_ok.groupby("ent").size().reset_index(name="num_adults")

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
    counts["ent_int"] = counts["ent"].astype("Int64")
    counts["state"] = counts["ent_int"].map(state_map).fillna(counts["ent_int"].astype(str))

    # Above-average filter
    avg_count = counts["num_adults"].mean()
    result = counts[counts["num_adults"] > avg_count].copy()

    # Final formatting
    result = result[["state", "num_adults"]].sort_values(by="num_adults", ascending=False).reset_index(drop=True)
    return result