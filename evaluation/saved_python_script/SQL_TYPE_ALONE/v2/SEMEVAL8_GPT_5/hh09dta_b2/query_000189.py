import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_inr = tables["ii_inr"].copy()

    # Normalize individual IDs for matching
    df_portad["ls_num"] = pd.to_numeric(df_portad["ls"], errors="coerce")
    df_inr["ls_num"] = pd.to_numeric(df_inr["ls"], errors="coerce")

    # Filter: respondent with individual ID 2 reported producing/selling dairy (inr02a == 1)
    df_inr_filt = df_inr[(df_inr["ls_num"] == 2) & (df_inr["inr02a"] == 1)]

    # Merge to get state and age of the same individual (ID 2) and ensure adulthood (edad >= 18)
    merged = df_inr_filt.merge(
        df_portad[["folio", "ent", "edad", "ls_num"]],
        on=["folio", "ls_num"],
        how="inner"
    )
    merged = merged[(merged["edad"] >= 18) & (merged["inr03a"].notna())]

    if merged.empty:
        return pd.DataFrame(columns=["state", "mean_quantity_12m_dairy"])

    # Map state codes to names
    ent_map = {
        2.0: "Baja California",
        3.0: "Baja California Sur",
        4.0: "Campeche",
        5.0: "Coahuila",
        6.0: "Colima",
        7.0: "Chiapas",
        9.0: "Distrito Federal",
        10.0: "Durango",
        11.0: "Guanajuato",
        12.0: "Guerrero",
        13.0: "Hidalgo",
        14.0: "Jalisco",
        15.0: "Estado de México",
        16.0: "Michoacán",
        17.0: "Morelos",
        18.0: "Nayarit",
        19.0: "Nuevo León",
        20.0: "Oaxaca",
        21.0: "Puebla",
        22.0: "Querétaro",
        25.0: "Sinaloa",
        26.0: "Sonora",
        28.0: "Tamaulipas",
        29.0: "Tlaxcala",
        30.0: "Veracruz",
        31.0: "Yucatán",
        32.0: "Zacatecas",
    }
    merged["state"] = merged["ent"].map(ent_map).fillna(merged["ent"].astype(str))

    # Compute state means and national mean
    state_means = (
        merged.groupby("state", as_index=False)["inr03a"]
        .mean()
        .rename(columns={"inr03a": "mean_quantity_12m_dairy"})
    )
    national_mean = merged["inr03a"].mean()

    # Filter states above national average
    result = state_means[state_means["mean_quantity_12m_dairy"] > national_mean].copy()
    result = result.sort_values("mean_quantity_12m_dairy", ascending=False).reset_index(drop=True)

    return result