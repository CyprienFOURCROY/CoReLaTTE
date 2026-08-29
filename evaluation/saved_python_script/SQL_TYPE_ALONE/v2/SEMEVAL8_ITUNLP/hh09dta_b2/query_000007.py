import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    # Filter households that feel unsafe or very unsafe at home
    unsafe_codes = {3.0, 4.0}
    df_unsafe = df_vlh[df_vlh["vlh04"].isin(unsafe_codes)]

    # Keep individuals with a valid interviewed age
    df_people = df_portad[["folio", "ent", "edad"]].dropna(subset=["edad", "ent"])

    # Merge individuals with unsafe households
    dfm = df_people.merge(df_unsafe, on="folio", how="inner")

    # Group by state and compute counts and average age
    grouped = dfm.groupby("ent").agg(n=("edad", "size"), average_age=("edad", "mean")).reset_index()

    # Keep only states with at least 10 individuals
    grouped = grouped[grouped["n"] >= 10]

    # Map state codes to names
    state_map = {
        2.0: "Baja California",
        3.0: "Baja California Sur",
        4.0: "Campeche",
        5.0: "Coahuila",
        6.0: "Colima",
        7.0: "Chiapas",
        9.0: "Distrito Federal",
        10.0: "Durango",
        11.0: "Guanajuato",
        12.0: "Guerrero",
        13.0: "Hidalgo",
        14.0: "Jalisco",
        15.0: "Estado de México",
        16.0: "Michoacán",
        17.0: "Morelos",
        18.0: "Nayarit",
        19.0: "Nuevo León",
        20.0: "Oaxaca",
        21.0: "Puebla",
        22.0: "Querétaro",
        25.0: "Sinaloa",
        26.0: "Sonora",
        28.0: "Tamaulipas",
        29.0: "Tlaxcala",
        30.0: "Veracruz",
        31.0: "Yucatán",
        32.0: "Zacatecas",
    }
    grouped["state"] = grouped["ent"].map(state_map).fillna(grouped["ent"].astype(str))

    # Sort by average age descending
    result = grouped.sort_values("average_age", ascending=False)[["state", "average_age"]].reset_index(drop=True)

    return result