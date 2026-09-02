def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_ah = tables["ii_ah"]

    # Step 1: Find households where at least one member owns both an electronic device and a washing machine/stove
    # ah03e: owns electronic device? (1: Yes), ah03f: owns wash machine/stove? (1: Yes)
    hh_with_electronic_and_wash = df_ah[
        (df_ah["ah03e"] == 1.0) & (df_ah["ah03f"] == 1.0)
    ]["folio"].unique()

    # Step 2: Find households where at least one member owns or shares a non-ag business (nna01 == 1)
    hh_with_nonag_business = df_nna[df_nna["nna01"] == 1.0]["folio"].unique()

    # Step 3: Households that satisfy both conditions
    eligible_hh = set(hh_with_electronic_and_wash) & set(hh_with_nonag_business)

    # Step 4: Filter adults (18+) in those households
    adults = df_portad[
        (df_portad["folio"].isin(eligible_hh)) &
        (df_portad["edad"] >= 18)
    ].copy()

    # Step 5: Group by state and calculate average age and count
    result = (
        adults.groupby("ent")
        .agg(
            average_age=("edad", "mean"),
            num_adults=("edad", "count")
        )
        .reset_index()
    )

    # Step 6: Get top 10 states by average age
    result = result.sort_values("average_age", ascending=False).head(10)

    # Map state codes to names (from metadata)
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
    result = result[["state", "average_age", "num_adults"]].reset_index(drop=True)
    return result