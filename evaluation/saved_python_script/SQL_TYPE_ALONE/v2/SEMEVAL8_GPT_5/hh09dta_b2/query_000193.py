import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()
    df_crh = tables["ii_crh"].copy()

    # Adults 18+
    adults = df_portad.loc[df_portad["edad"] >= 18, ["ent", "folio"]].dropna(subset=["folio"])
    
    # Households that completely disagree their locality is close (vlh01k == 4)
    hh_not_close = df_vlh.loc[df_vlh["vlh01k"] == 4.0, ["folio"]].dropna().drop_duplicates()

    # Households with total debts + interests > 5000 using value or brackets
    debt_mask = (df_crh["crh04_2"] > 5000) | (df_crh["crh04c"] == 2.0) | (df_crh["crh04d"] == 2.0)
    hh_debt = df_crh.loc[debt_mask, ["folio"]].dropna().drop_duplicates()

    # Eligible households: satisfy both conditions
    eligible_hh = pd.merge(hh_not_close, hh_debt, on="folio", how="inner")

    # Adults living in eligible households
    adults_in_eligible = pd.merge(adults, eligible_hh, on="folio", how="inner")

    # Group by state and count adults
    result = (
        adults_in_eligible.groupby("ent", as_index=False)
        .size()
        .rename(columns={"size": "num_adults"})
        .sort_values("ent")
        .reset_index(drop=True)
    )

    return result