import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_nna = tables["ii_nna"].copy()
    df_vlh = tables["ii_vlh"].copy()
    df_su = tables["ii_su"].copy()

    # Household to state mapping
    df_ent = df_portad[["folio", "ent"]].dropna(subset=["ent"]).drop_duplicates(subset=["folio"])

    # Conditions
    hv = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]].drop_duplicates()
    hn = df_nna[df_nna["nna01"] == 1.0][["folio"]].drop_duplicates()
    hs = df_su[df_su["su01"] == 3.0][["folio"]].drop_duplicates()

    # Households meeting all conditions
    folio_common = hv.merge(hn, on="folio", how="inner").merge(hs, on="folio", how="inner")

    # Attach state
    df_cond = folio_common.merge(df_ent, on="folio", how="inner")

    # Counts per state (households)
    counts = df_cond.groupby("ent", as_index=False).agg(count=("folio", "nunique"))

    # Include zero-count states present in data
    unique_ents = pd.DataFrame({"ent": pd.Series(df_ent["ent"].dropna().unique())})
    counts_all = unique_ents.merge(counts, on="ent", how="left")
    counts_all["count"] = counts_all["count"].fillna(0).astype(int)

    # Average across all states
    avg_count = counts_all["count"].mean()

    # Filter for Oaxaca (20) and Puebla (21) with below-average counts
    target_ents = [20.0, 21.0]
    target_counts = counts_all[counts_all["ent"].isin(target_ents)].copy()
    below_avg = target_counts[target_counts["count"] < avg_count].copy()

    # Map to state names
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
    below_avg["state"] = below_avg["ent"].astype(int).map(ent_to_state)

    return below_avg[["state", "count"]].reset_index(drop=True)