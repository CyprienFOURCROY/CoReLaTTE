def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Merge on 'folio'
    df = pd.merge(df_portad, df_vlh, on="folio", how="inner")

    # Filter: households who answered 'No' to knowing a family/friend robbed in last 12 months
    # vlh10a == 3 means 'No'
    df = df[df["vlh10a"] == 3.0]

    # Only keep rows with valid 'vlh04' (Do you feel safe at home?)
    # 1: Very safe, 2: Safe, 3: Unsafe, 4: Very unsafe
    df = df[df["vlh04"].isin([1.0, 2.0, 3.0, 4.0])]

    # Compute national average for this group
    national_avg = df["vlh04"].mean()

    # Group by state ('ent'), compute average and count
    state_stats = (
        df.groupby("ent")
        .agg(avg_vlh04=("vlh04", "mean"), household_count=("folio", "count"))
        .reset_index()
    )

    # Only states with avg_vlh04 >= 3 and above national average
    result = state_stats[(state_stats["avg_vlh04"] >= 3) & (state_stats["avg_vlh04"] > national_avg)]

    # Rank from highest (least safe) to lowest
    result = result.sort_values(by="avg_vlh04", ascending=False)

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

    # Reorder columns
    result = result[["state", "avg_vlh04", "household_count"]]

    # Reset index for clean output
    result = result.reset_index(drop=True)

    return result