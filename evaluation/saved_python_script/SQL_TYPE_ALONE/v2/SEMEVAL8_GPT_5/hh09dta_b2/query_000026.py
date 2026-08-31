import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"].copy()

    # Map folio to state (ent)
    ent_by_folio = (
        df_portad[["folio", "ent"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"])
    )

    # Keep relevant SU columns and merge
    su_cols = df_su[["folio", "su01", "su234"]].copy()
    merged = su_cols.merge(ent_by_folio, on="folio", how="inner")

    # Households that use a plot/land for sowing/farming
    merged = merged[merged["su01"] == 1]

    # Compute overall average seeds expense among such households
    overall_avg = merged["su234"].mean()

    # Average seeds expense by state
    state_means = (
        merged.groupby("ent", dropna=True, as_index=False)["su234"]
        .mean()
        .rename(columns={"su234": "avg_seeds_expense"})
    )

    # Filter states: avg > 1000 and >= overall average
    if pd.isna(overall_avg):
        filtered = state_means[state_means["avg_seeds_expense"] > 1000].copy()
    else:
        filtered = state_means[
            (state_means["avg_seeds_expense"] > 1000)
            & (state_means["avg_seeds_expense"] >= overall_avg)
        ].copy()

    # Rank by average expense (highest to lowest)
    if not filtered.empty:
        filtered = filtered.sort_values(by=["avg_seeds_expense", "ent"], ascending=[False, True])
        filtered["rank"] = filtered["avg_seeds_expense"].rank(method="dense", ascending=False).astype("int64")
    else:
        filtered["rank"] = pd.Series(dtype="int64")

    # Optional: state name mapping for readability
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

    filtered["ent"] = filtered["ent"].astype("Int64")
    filtered["state"] = filtered["ent"].map(state_map)

    # Order columns
    return filtered[["state", "ent", "avg_seeds_expense", "rank"]]