import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_crh = tables["ii_crh"]

    # Oaxaca households (state 20) with at least one adult (edad >= 18)
    oax_adults = df_portad[
        (df_portad["ent"] == 20.0) & (df_portad["edad"].notna()) & (df_portad["edad"] >= 18)
    ]
    oax_adult_folios = pd.Index(oax_adults["folio"].dropna().unique())

    # Households with a member who owns/shares a non-ag business
    nna_yes = df_nna[(df_nna["nna01"] == 1.0) & (df_nna["folio"].notna())]
    target_folios = pd.Index(nna_yes[nna_yes["folio"].isin(oax_adult_folios)]["folio"].unique())

    # From those households, select those that both owed and paid on credit/loans in last 12 months
    crh_subset = df_crh[df_crh["folio"].isin(target_folios)].copy()
    cond_owed = (crh_subset["crh02_1"] == 1.0) & (crh_subset["crh02_2"].notna())
    cond_paid = (crh_subset["crh03_1"] == 1.0) & (crh_subset["crh03_2"].notna())
    both_owed_paid = crh_subset[cond_owed & cond_paid].copy()

    if both_owed_paid.empty:
        return pd.DataFrame(columns=["folio", "amount_owed_pesos", "amount_paid_pesos"])

    # Compute the group's average amount paid and filter those who paid more than average
    avg_paid = both_owed_paid["crh03_2"].mean()
    above_avg_paid = both_owed_paid[both_owed_paid["crh03_2"] > avg_paid].copy()

    result = (
        above_avg_paid[["folio", "crh02_2", "crh03_2"]]
        .rename(columns={"crh02_2": "amount_owed_pesos", "crh03_2": "amount_paid_pesos"})
        .sort_values(by="amount_paid_pesos", ascending=False)
        .reset_index(drop=True)
    )

    return result