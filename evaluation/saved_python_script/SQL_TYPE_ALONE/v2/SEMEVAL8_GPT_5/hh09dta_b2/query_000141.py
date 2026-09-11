import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()

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

    # Households that own electronic devices and reported their value
    mask = (df_ah["ah03e"] == 1.0) & (df_ah["ah04e_1"] == 1.0) & (df_ah["ah04e_2"].notna())
    df_ah_val = df_ah.loc[mask, ["folio", "ah04e_2"]].dropna(subset=["folio"])

    # One record per household (take max in case of duplicates)
    df_hh = df_ah_val.groupby("folio", as_index=False)["ah04e_2"].max()

    # State per household
    df_ent = df_portad[["folio", "ent"]].dropna(subset=["folio"]).drop_duplicates(subset=["folio"], keep="first")

    df_merged = df_hh.merge(df_ent, on="folio", how="left")
    df_merged = df_merged[df_merged["ent"].notna()]
    df_merged["state"] = df_merged["ent"].map(state_map)
    df_merged = df_merged[df_merged["state"].notna()]

    # Overall average across all such households
    overall_avg = df_merged["ah04e_2"].mean()

    # State-level stats
    result = (
        df_merged.groupby("state")
        .agg(num_households=("folio", "nunique"), average_value=("ah04e_2", "mean"))
        .reset_index()
    )

    # Apply thresholds
    result = result[result["num_households"] >= 30]
    result = result[result["average_value"] > overall_avg]

    result = result.sort_values(["average_value", "state"], ascending=[False, True]).reset_index(drop=True)

    return result