import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_ah = tables["ii_ah"][["folio", "ah03d"]].copy()

    # Households where residents feel safe or very safe at home
    hh_safe = (
        df_vlh[df_vlh["vlh04"].isin([1.0, 2.0])]
        .dropna(subset=["folio"])
        [["folio"]]
        .drop_duplicates()
    )

    # Households where at least one household member owns a motor vehicle
    hh_motor = (
        df_ah[df_ah["ah03d"] == 1.0]
        .dropna(subset=["folio"])
        [["folio"]]
        .drop_duplicates()
    )

    # Intersection: households satisfying both conditions
    eligible_hh = hh_safe.merge(hh_motor, on="folio", how="inner").drop_duplicates()

    # Attach state (ent) to households
    hh_ent = (
        df_portad.dropna(subset=["folio", "ent"])
        [["folio", "ent"]]
        .drop_duplicates()
    )

    merged = eligible_hh.merge(hh_ent, on="folio", how="left")
    merged = merged.dropna(subset=["ent"])
    merged = merged[["folio", "ent"]].drop_duplicates()
    merged["ent"] = merged["ent"].astype(int)

    # Count households per state
    counts = (
        merged.groupby("ent", as_index=False)
        .agg(households=("folio", "nunique"))
    )

    # Filter states with at least 100 households
    counts = counts[counts["households"] >= 100].copy()

    # Map state codes to names
    ent_to_state = {
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
    counts["state"] = counts["ent"].map(ent_to_state)

    # Final sorting by count descending
    result = counts.sort_values(by="households", ascending=False)[["state", "households"]].reset_index(drop=True)

    return result