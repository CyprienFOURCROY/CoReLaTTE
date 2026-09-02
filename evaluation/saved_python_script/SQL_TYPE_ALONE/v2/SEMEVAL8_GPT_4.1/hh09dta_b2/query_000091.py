def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Merge to get state info
    df = df_in.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Filter: households that received Liconsa milk in last 12 months (in03a == 1)
    df_liconsa = df[df["in03a"] == 1]

    # Only keep rows with non-null state and in02a10 (amount received directly from Other Government Program)
    df_liconsa = df_liconsa[~df_liconsa["ent"].isnull()]

    # Group by state, count households, and compute average in02a10 (amount received directly from Other Government Program)
    grouped = (
        df_liconsa.groupby("ent")
        .agg(
            n_households=("folio", "count"),
            avg_in02a10=("in02a10", "mean")
        )
        .reset_index()
    )

    # Only states with at least 25 such households
    grouped = grouped[grouped["n_households"] >= 25]

    # Compute overall average across those states (weighted by household count)
    overall_avg = grouped["avg_in02a10"].mean()

    # Filter states with average above overall average
    result = grouped[grouped["avg_in02a10"] > overall_avg].copy()

    # Rank by avg_in02a10 descending
    result = result.sort_values("avg_in02a10", ascending=False).reset_index(drop=True)

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

    # Reorder columns and reset index for ranking
    result = result[["state", "n_households", "avg_in02a10"]].reset_index(drop=True)
    result["rank"] = result["avg_in02a10"].rank(method="dense", ascending=False).astype(int)
    result = result.sort_values("rank").reset_index(drop=True)

    return result[["rank", "state", "n_households", "avg_in02a10"]]