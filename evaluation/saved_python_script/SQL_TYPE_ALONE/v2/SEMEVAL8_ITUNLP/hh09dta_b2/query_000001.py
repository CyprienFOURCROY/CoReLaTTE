import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Household -> state mapping (use first occurrence per folio)
    df_ent = (
        df_portad[["folio", "ent"]]
        .drop_duplicates(subset=["folio"])
        .copy()
    )

    # Merge household safety/violence with state
    df = df_vlh.merge(df_ent, on="folio", how="left")

    # Filter: Yes to knowing family/friend robbed in last 5 years
    df_yes = df[df["vlh08a"] == 1.0].copy()

    # Clean vlh06 (9 = NA)
    df_yes["vlh06_clean"] = df_yes["vlh06"].where(df_yes["vlh06"] != 9.0)

    # Prepare state code as integer (nullable)
    df_yes["ent_code"] = df_yes["ent"].astype("Int64")

    # Aggregate by state
    agg = (
        df_yes.groupby("ent_code", dropna=True)
        .agg(
            avg_feel_safe_at_home=("vlh04", "mean"),
            avg_leave_lights_as_security=("vlh06_clean", "mean"),
            households=("folio", "nunique"),
        )
        .reset_index()
    )

    # Keep states with at least 5 households
    agg = agg[agg["households"] >= 5].copy()

    # Order from safest (lower avg_feel_safe_at_home) to least safe
    agg = agg.sort_values(
        by=["avg_feel_safe_at_home", "avg_leave_lights_as_security"],
        ascending=[True, True],
        kind="mergesort",
    )

    # Optional: map state codes to names from provided metadata
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
    agg["state"] = agg["ent_code"].map(lambda x: ent_to_state.get(int(x)) if pd.notna(x) else None)
    agg = agg.rename(columns={"ent_code": "ent"})

    # Final column order
    return agg[["state", "ent", "avg_feel_safe_at_home", "avg_leave_lights_as_security", "households"]]