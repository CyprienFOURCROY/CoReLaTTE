import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Households that received Liconsa milk in last 12 months
    df_in_liconsa = df_in.loc[df_in["in03a"] == 1.0, ["folio"]].drop_duplicates()

    # Household-level state (ent) and indicator for at least one person aged 50+
    tmp = df_portad[["folio", "edad", "ent"]].copy()
    tmp["has_50plus"] = tmp["edad"] >= 50
    hh_portad = tmp.groupby("folio", as_index=False).agg(
        has_50plus=("has_50plus", "max"),
        ent=("ent", "first")
    )
    hh_portad = hh_portad.loc[hh_portad["has_50plus"]]

    # Merge eligibility (Liconsa + 50+) and bring robbery count since 2005
    eligible = df_in_liconsa.merge(hh_portad, on="folio", how="inner")
    eligible = eligible.merge(df_vlh[["folio", "vlh18a"]], on="folio", how="inner")
    eligible = eligible.loc[eligible["vlh18a"].notna()]

    if eligible.empty:
        return pd.DataFrame(columns=["state", "avg_robberies_since_2005", "households"])

    # Map state codes to names (fallback to code string if not in mapping)
    ent_mapping = {
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
    eligible["ent_code"] = eligible["ent"].astype("Int64")
    eligible["state"] = eligible["ent_code"].map(ent_mapping).fillna(eligible["ent_code"].astype(str))

    # Aggregate by state
    res = (
        eligible.groupby("state", as_index=False)
        .agg(
            avg_robberies_since_2005=("vlh18a", "mean"),
            households=("folio", "nunique"),
        )
        .sort_values(["avg_robberies_since_2005", "state"], ascending=[False, True])
        .head(5)
        .reset_index(drop=True)
    )

    return res