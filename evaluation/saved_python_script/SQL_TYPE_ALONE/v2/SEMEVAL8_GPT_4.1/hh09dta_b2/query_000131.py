def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_crh = tables["ii_crh"]
    df_su = tables["ii_su"]

    # 1. Households that use a plot/land for sowing/farming/vegetables (su01 == 1)
    df_su_plot = df_su[df_su["su01"] == 1.0][["folio"]]

    # 2. Households that did NOT produce/sell meat in last 12 months (inr02c == 3)
    df_inr_no_meat = df_inr[df_inr["inr02c"] == 3.0][["folio"]]

    # 3. Intersection: households that satisfy both
    folios_plot_no_meat = pd.Series(
        np.intersect1d(df_su_plot["folio"].values, df_inr_no_meat["folio"].values)
    )

    # 4. Get state for each household (use only one row per folio)
    df_portad_folio = df_portad.drop_duplicates("folio")[["folio", "ent"]]

    # 5. Get crh03_2 (amount paid in last 12 months) for each household
    df_crh_amt = df_crh[["folio", "crh03_2"]]

    # 6. Merge all info
    df = pd.DataFrame({"folio": folios_plot_no_meat})
    df = df.merge(df_portad_folio, on="folio", how="left")
    df = df.merge(df_crh_amt, on="folio", how="left")

    # 7. Only keep households with a valid state and a valid crh03_2 (amount paid)
    df = df[df["ent"].notna()]
    df = df[df["crh03_2"].notna()]

    # 8. Group by state, count households and get max amount paid
    grouped = df.groupby("ent").agg(
        household_count=("folio", "count"),
        max_paid=("crh03_2", "max")
    ).reset_index()

    # 9. Only states with at least 25 such households
    grouped = grouped[grouped["household_count"] >= 25]

    # 10. Compute overall average of these state-level maxima
    overall_avg_max = grouped["max_paid"].mean()

    # 11. Filter states with max_paid above the overall average
    result = grouped[grouped["max_paid"] > overall_avg_max].copy()

    # 12. Map state codes to names
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

    # 13. Select and order columns
    result = result[["state", "household_count", "max_paid"]].sort_values("max_paid", ascending=False).reset_index(drop=True)

    return result