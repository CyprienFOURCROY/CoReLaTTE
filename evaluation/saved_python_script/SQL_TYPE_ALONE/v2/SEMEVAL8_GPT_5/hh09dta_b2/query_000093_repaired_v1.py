import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]]
    df_in = tables["ii_in"][["folio", "in01a10_1", "in02a10"]]
    df_crh = tables["ii_crh"][["folio", "crh03_1", "crh03_2", "crh04_2"]]

    # Households in Oaxaca (ent == 20) with at least one member aged 70+
    oax_70p_folios = (
        df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 70)]
        .dropna(subset=["folio"])
        .loc[:, "folio"]
        .unique()
    )

    # Received income from an Other Government Program
    received_other_gov_mask = (df_in["in01a10_1"] == 1.0) | (df_in["in02a10"].notna() & (df_in["in02a10"] > 0))
    other_gov_folios = df_in.loc[received_other_gov_mask, "folio"].dropna().unique()

    # Reported an amount paid on credit/loans in the last year and have total debt value
    crh_filt = df_crh[(df_crh["crh03_1"] == 1.0) & (df_crh["crh04_2"].notna())]

    # Intersection of conditions
    selected = crh_filt[
        crh_filt["folio"].isin(oax_70p_folios) &
        crh_filt["folio"].isin(other_gov_folios)
    ].copy()

    if selected.empty:
        return pd.DataFrame(columns=["folio", "total_debt_pesos"])

    mean_debt = selected["crh04_2"].mean()

    result = (
        selected[selected["crh04_2"] > mean_debt][["folio", "crh04_2"]]
        .rename(columns={"crh04_2": "total_debt_pesos"})
        .sort_values(by="total_debt_pesos", ascending=False)
        .reset_index(drop=True)
    )

    return result