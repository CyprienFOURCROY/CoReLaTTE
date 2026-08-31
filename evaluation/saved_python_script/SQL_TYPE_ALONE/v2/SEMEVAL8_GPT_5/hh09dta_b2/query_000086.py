import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_vlh = tables["ii_vlh"].copy()
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()

    # Household-level state (ent) per folio
    df_portad = df_portad.dropna(subset=["folio"])
    hh_state = df_portad.groupby("folio", as_index=False).agg(ent=("ent", "first"))
    hh_state = hh_state.dropna(subset=["ent"])

    # Filter households: feel unsafe or very unsafe (3 or 4) and no forced home entry since 2005 (vlh12a_c == 3)
    cond_unsafe = df_vlh["vlh04"].isin([3.0, 4.0])
    cond_no_forced_since_2005 = df_vlh["vlh12a_c"] == 3.0
    hh_filtered = df_vlh.loc[cond_unsafe & cond_no_forced_since_2005, ["folio", "vlh04"]].dropna(subset=["folio"])

    # Merge with state
    merged = hh_filtered.merge(hh_state, on="folio", how="left").dropna(subset=["ent"])
    merged["ent"] = merged["ent"].astype(int)

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
        32: "Zacatecas",
    }
    merged = merged[merged["ent"].isin(list(state_map.keys()))]

    # National mean (among filtered households)
    national_mean = merged["vlh04"].mean()

    # State-level stats
    state_stats = (
        merged.groupby("ent")
        .agg(mean_score=("vlh04", "mean"), n_households=("folio", "nunique"))
        .reset_index()
    )

    # Filter states with at least 30 households and above-national-average mean
    state_stats = state_stats[state_stats["n_households"] >= 30]
    state_stats = state_stats[state_stats["mean_score"] > national_mean]

    # Add state names and order
    state_stats["state"] = state_stats["ent"].map(state_map)
    state_stats = state_stats.sort_values(by=["mean_score", "n_households"], ascending=[False, False])

    return state_stats[["state", "ent", "mean_score", "n_households"]].reset_index(drop=True)