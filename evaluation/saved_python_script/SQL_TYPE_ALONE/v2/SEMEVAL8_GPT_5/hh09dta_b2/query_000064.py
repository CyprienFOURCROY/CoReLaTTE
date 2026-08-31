import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_inr = tables["ii_inr"].copy()

    # Households that answered yes or no to receiving Liconsa milk
    hh_liconsa = df_in[df_in["in03a"].isin([1.0, 3.0])][["folio"]].dropna().drop_duplicates()

    # Households that reported producing/selling dairy products in the last 12 months
    hh_dairy = df_inr[df_inr["inr02a"] == 1.0][["folio"]].dropna().drop_duplicates()

    # Intersection of both household sets
    hh_selected = pd.merge(hh_liconsa, hh_dairy, on="folio", how="inner")

    # Adults (18+) in person-level data
    adults = df_portad[(df_portad["edad"] >= 18) & df_portad["folio"].notna() & df_portad["ent"].notna()].copy()
    adults["ent_int"] = adults["ent"].astype("int64")

    # All states present among adults (to include zeros in average)
    all_states = pd.DataFrame({"ent_int": sorted(adults["ent_int"].unique())})

    # Adults living in selected households
    adults_selected = adults.merge(hh_selected, on="folio", how="inner")
    counts = adults_selected.groupby("ent_int").size().rename("adult_count").reset_index()

    # Include states with zero counts
    full_counts = all_states.merge(counts, on="ent_int", how="left").fillna({"adult_count": 0})
    full_counts["adult_count"] = full_counts["adult_count"].astype(int)

    # Average across states (including zeros)
    avg_count = full_counts["adult_count"].mean()

    # States with above-average counts
    above = full_counts[full_counts["adult_count"] > avg_count].copy()

    # Map state codes to names
    code_to_name = {
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
    above["state"] = above["ent_int"].map(code_to_name).fillna(above["ent_int"].astype(str))

    result = above[["state", "adult_count"]].sort_values(["adult_count", "state"], ascending=[False, True]).reset_index(drop=True)
    return result