import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()

    # Identify households with at least one resident aged 70+
    age_by_folio = (
        df_portad.groupby("folio", as_index=False)
        .agg(edad=("edad", "max"), ent=("ent", "first"))
    )
    age70 = age_by_folio[age_by_folio["edad"] >= 70]

    # Households that reported receiving income from '70 y más' in the last 12 months
    hh_70prog = (
        df_in.loc[df_in["in01a11_1"] == 1.0, ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates()
    )

    # Intersection: households meeting both conditions
    qualified = age70.merge(hh_70prog, on="folio", how="inner")

    # Count households per state
    counts = (
        qualified.groupby("ent", as_index=False)["folio"]
        .nunique()
        .rename(columns={"folio": "num_households"})
    )

    # Average across states (among states with at least one such household)
    avg_count = counts["num_households"].mean()

    # States with at least the average number of such households
    result = counts[counts["num_households"] >= avg_count].copy()

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
    result["state"] = result["ent"].map(state_map)

    result = result.rename(columns={"ent": "state_code", "num_households": "households"})
    result = result[["state_code", "state", "households"]].sort_values(
        ["households", "state_code"], ascending=[False, True]
    ).reset_index(drop=True)

    return result