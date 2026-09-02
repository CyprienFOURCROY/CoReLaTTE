def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_nna = tables["ii_nna"]

    # 1. Households where at least one member produced/sold dairy products in last 12 months
    # inr02a == 1 means Yes
    dairy_households = df_inr[df_inr["inr02a"] == 1][["folio"]].drop_duplicates()

    # 2. Merge with ii_portad to get state and age
    # We'll use the household head's age as "household age" (assuming one row per folio in ii_portad)
    # If multiple, take the mean age per household
    portad_folios = df_portad[["folio", "ent", "edad"]]
    dairy_households = dairy_households.merge(portad_folios, on="folio", how="left")

    # 3. For each household, get average age (if multiple rows per folio)
    hh_age = dairy_households.groupby(["folio", "ent"], as_index=False)["edad"].mean()

    # 4. For each household, check if at least one member owns/shares non-ag business (nna01 == 1)
    nna = df_nna[["folio", "nna01"]]
    nna_nonag = nna[nna["nna01"] == 1].groupby("folio").size().reset_index(name="has_nonag")
    nna_nonag["has_nonag"] = 1  # mark as 1 if present

    # Merge with hh_age
    hh = hh_age.merge(nna_nonag[["folio", "has_nonag"]], on="folio", how="left")
    hh["has_nonag"] = hh["has_nonag"].fillna(0).astype(int)

    # 5. For each state, aggregate:
    # (a) number of such households
    # (b) average household age among them
    # (c) number of those households with at least one member who owns/shares non-ag business
    result = (
        hh.groupby("ent")
        .agg(
            num_households=("folio", "nunique"),
            avg_household_age=("edad", "mean"),
            num_with_nonag_business=("has_nonag", "sum"),
        )
        .reset_index()
    )

    # 6. Get top 10 states by number of such households
    result = result.sort_values("num_households", ascending=False).head(10)

    # 7. Map state codes to names
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
    result = result[["state", "num_households", "avg_household_age", "num_with_nonag_business"]]

    return result.reset_index(drop=True)