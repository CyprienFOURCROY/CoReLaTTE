def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]

    # Filter for adults (age 18+) with individual ID 2
    df_adults = df_portad[(df_portad["edad"] >= 18) & (df_portad["ls"] == "02")]

    # Merge with inr to get only those with matching folio and ls
    df_merged = df_adults.merge(
        df_inr,
        left_on=["folio", "ls"],
        right_on=["folio", "ls"],
        how="inner"
    )

    # Only keep those who reported producing/selling dairy products (inr02a == 1)
    df_merged = df_merged[df_merged["inr02a"] == 1]

    # Only keep households with a non-null, non-negative quantity sold in last 12 months (inr03a)
    df_merged = df_merged[~df_merged["inr03a"].isna()]

    # Group by household (folio), take the sum of inr03a per household (should be one per household)
    df_household = df_merged.groupby(["folio", "ent"], as_index=False)["inr03a"].sum()

    # Compute national mean
    national_mean = df_household["inr03a"].mean()

    # Compute mean per state
    df_state = df_household.groupby("ent", as_index=False)["inr03a"].mean()

    # Only keep states with mean above national mean
    df_above = df_state[df_state["inr03a"] > national_mean].copy()

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
    df_above["state"] = df_above["ent"].map(state_map)
    df_above = df_above.rename(columns={"inr03a": "mean_quantity_12mo"})
    df_above = df_above[["state", "mean_quantity_12mo"]].reset_index(drop=True)
    return df_above