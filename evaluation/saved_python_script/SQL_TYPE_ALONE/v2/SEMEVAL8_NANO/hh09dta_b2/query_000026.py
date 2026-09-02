def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_su = tables["ii_su"]

    # Filter households that use a plot/land for sowing/farming
    df_su_farming = df_su[df_su["su01"] == 1]

    # Merge with household info to get 'ent' (state)
    df_merged = df_su_farming.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Merge with expense in seeds
    df_merged = df_merged.merge(df_su[["folio", "su234"]]], on="folio", how="left")

    # Filter households with expense in seeds > 1000
    df_expensive_seeds = df_merged[df_merged["su234"] > 1000]

    # Calculate overall average expense in seeds for households that use land for farming
    overall_avg = df_su[df_su["su01"] == 1]["su234"].mean()

    # Filter households with expense in seeds >= overall average
    df_final = df_expensive_seeds[df_expensive_seeds["su234"] >= overall_avg]

    # Group by 'ent' (state) and compute mean expense
    state_expenses = (
        df_final.groupby("ent")["su234"]
        .mean()
        .reset_index()
        .rename(columns={"ent": "state_code", "su234": "avg_expense"})
    )

    # Filter states with average expense > 1000 (already ensured in df_final, but double check)
    # (This is redundant since we already filtered, but kept for clarity)
    state_expenses = state_expenses[state_expenses["avg_expense"] > 1000]

    # Rank states by average expense descending
    state_expenses = state_expenses.sort_values(by="avg_expense", ascending=False).reset_index(drop=True)

    # Map 'ent' codes to state names for clarity (optional, but useful)
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
        32: "Zacatecas"
    }
    state_expenses["state_name"] = state_expenses["state_code"].map(ent_to_state)

    # Select relevant columns
    result = state_expenses[["state_name", "avg_expense"]]

    return result