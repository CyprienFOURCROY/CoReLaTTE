import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].dropna(subset=["folio"]).drop_duplicates(subset=["folio"])
    df_nna = tables["ii_nna"][["folio", "nna01"]].dropna(subset=["folio"]).drop_duplicates(subset=["folio"])
    df_crh = tables["ii_crh"][["folio", "crh02_1", "crh02_2", "crh03_1", "crh03_2"]].dropna(subset=["folio"])

    # Households with a member owning/sharing a non-ag business
    df_nna_yes = df_nna[df_nna["nna01"] == 1.0][["folio"]].drop_duplicates()

    # Average borrowed among indebted households (with value)
    indebted = df_crh[(df_crh["crh02_1"] == 1.0) & (df_crh["crh02_2"].notna())]
    avg_borrowed = float(indebted["crh02_2"].mean()) if not indebted.empty else float("nan")

    # Households that paid more than they borrowed and more than the average borrowed
    df_paid = df_crh[
        (df_crh["crh02_1"] == 1.0)
        & (df_crh["crh03_1"] == 1.0)
        & (df_crh["crh02_2"].notna())
        & (df_crh["crh03_2"].notna())
    ].copy()

    if pd.notna(avg_borrowed):
        df_paid = df_paid[(df_paid["crh03_2"] > df_paid["crh02_2"]) & (df_paid["crh03_2"] > avg_borrowed)]
    else:
        df_paid = df_paid.iloc[0:0]

    # Eligible households: business owners and meet payment conditions
    eligible = pd.merge(df_paid[["folio"]].drop_duplicates(), df_nna_yes, on="folio", how="inner")

    # Attach state
    eligible = pd.merge(eligible, df_portad, on="folio", how="left")

    # Rank states by count of eligible households
    result = (
        eligible.groupby("ent", as_index=False)
        .agg(households_count=("folio", "nunique"))
        .sort_values(by=["households_count", "ent"], ascending=[False, True])
        .reset_index(drop=True)
    )

    # Optional: map state names for readability
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
    result["state"] = result["ent"].astype("Int64").map(state_map)

    return result[['ent', 'state', 'households_count']]