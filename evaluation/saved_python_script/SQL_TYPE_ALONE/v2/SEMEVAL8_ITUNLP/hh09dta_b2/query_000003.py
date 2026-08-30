import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()

    # Merge person-level with household-level info
    df = df_portad.merge(df_su, on="folio", how="inner").merge(df_crh, on="folio", how="inner")

    # Filters: adults 18+, households that use a plot (su01==1), and positive reported total debt (crh04_1==1 and crh04_2>0)
    df = df[
        (df["edad"] >= 18)
        & (df["su01"] == 1.0)
        & (df["crh04_1"] == 1.0)
        & (df["crh04_2"] > 0)
    ].copy()

    # Drop rows without a valid state code
    df = df.dropna(subset=["ent"]).copy()

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
    df["state_code"] = df["ent"].astype("Int64")
    df["state"] = df["state_code"].map(state_map)

    # Group by state and compute average debt (per adult record) and contributing adult records
    result = (
        df.groupby(["state_code", "state"], dropna=False)
        .agg(
            average_household_debt_pesos=("crh04_2", "mean"),
            adult_records=("folio", "size"),
        )
        .reset_index()
        .sort_values("average_household_debt_pesos", ascending=False)
        .head(10)
    )

    return result