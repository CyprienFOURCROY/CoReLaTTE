import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()

    # Prepare household-level age composition and state
    p = df_portad[["folio", "ent", "edad"]].dropna(subset=["folio"])
    def first_nonnull(s):
        s2 = s.dropna()
        return s2.iloc[0] if len(s2) else pd.NA

    hh_comp = (
        p.groupby("folio", as_index=False)
         .agg(
             ent=("ent", first_nonnull),
             has_senior=("edad", lambda s: (s >= 70).any()),
             has_child=("edad", lambda s: (s < 12).any())
         )
    )

    # Households with both a senior (70+) and a child (<12)
    hh_both = hh_comp[(hh_comp["has_senior"]) & (hh_comp["has_child"])].copy()
    hh_both = hh_both.dropna(subset=["ent"])
    hh_both["ent"] = hh_both["ent"].astype("Int64")

    # Liconsa milk received in last 12 months
    liconsa_yes = df_in.loc[df_in["in03a"] == 1, ["folio"]].dropna(subset=["folio"]).drop_duplicates()

    # Filter households by Liconsa
    eligible = hh_both.merge(liconsa_yes, on="folio", how="inner")

    if eligible.empty:
        return pd.DataFrame(columns=["state", "households"])

    # Count households per state
    state_counts = (
        eligible.groupby("ent")["folio"]
        .nunique()
        .reset_index(name="households")
    )

    # National average across states (mean of state counts)
    nat_avg = state_counts["households"].mean()

    above = state_counts[state_counts["households"] > nat_avg].copy()

    # Map state codes to names
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

    above["state"] = above["ent"].astype("Int64").map(ent_to_state)
    above["state"] = above["state"].fillna(above["ent"].astype(str))

    result = above[["state", "households"]].sort_values(
        by=["households", "state"], ascending=[False, True]
    ).reset_index(drop=True)

    return result