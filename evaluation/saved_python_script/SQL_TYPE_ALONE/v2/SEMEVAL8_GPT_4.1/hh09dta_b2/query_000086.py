def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Merge on household ID
    df = df_portad.merge(df_vlh, on="folio", how="inner")

    # Filter: households that report feeling unsafe or very unsafe at home
    # vlh04: 3 = Unsafe, 4 = Very unsafe
    mask_unsafe = df["vlh04"].isin([3.0, 4.0])

    # Filter: have NOT experienced a forced home entry since 2005
    # vlh12a_a: 1 = Yes, into the dwelling you currently live in (since 2005)
    # vlh12a_b: 2 = Yes, into another dwelling where you used to live (since 2005)
    # vlh12a_c: 3 = No (since 2005)
    # We want only those with vlh12a_c == 3 (No)
    mask_no_forced_entry = (df["vlh12a_c"] == 3.0)

    # Only keep rows that satisfy both conditions
    df_filtered = df[mask_unsafe & mask_no_forced_entry].copy()

    # Home safety scale: vlh04 (higher = more unsafe)
    # Group by state (ent)
    group = df_filtered.groupby("ent").agg(
        mean_home_safety=("vlh04", "mean"),
        household_count=("folio", "count")
    ).reset_index()

    # Only keep states with at least 30 such households
    group = group[group["household_count"] >= 30]

    # Compute national average mean (weighted by household count)
    # But since we want the mean of all relevant households, just take the mean of vlh04 in df_filtered
    national_mean = df_filtered["vlh04"].mean()

    # Keep only states with above-national-average mean
    group = group[group["mean_home_safety"] > national_mean]

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
    group["state"] = group["ent"].map(state_map)

    # Order by highest mean
    group = group.sort_values("mean_home_safety", ascending=False)

    # Select and reorder columns
    result = group[["state", "mean_home_safety", "household_count"]].reset_index(drop=True)

    return result