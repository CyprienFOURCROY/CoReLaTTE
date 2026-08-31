import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04", "vlh01k"]].copy()

    # Households in Oaxaca (ent == 20)
    oax_folios = (
        df_portad.loc[df_portad["ent"] == 20, ["folio"]]
        .drop_duplicates()
        .folio
    )

    # Positive total debt (including interest): crh04_1 == 1 and crh04_2 > 0
    m_debt = (df_crh["crh04_1"] == 1) & (df_crh["crh04_2"] > 0)
    debt_pos = (
        df_crh.loc[m_debt, ["folio", "crh04_2"]]
        .groupby("folio", as_index=False)["crh04_2"]
        .max()
        .rename(columns={"crh04_2": "debt_value"})
    )

    # Safety perception and locality close-knit disagreement
    vlh_flags = df_vlh.assign(
        unsafe=lambda x: x["vlh04"].isin([3, 4]),
        disagree_close=lambda x: x["vlh01k"].isin([3, 4]),
    ).groupby("folio", as_index=False).agg(
        unsafe_any=("unsafe", "any"),
        disagree_any=("disagree_close", "any"),
    )

    # Merge and filter conditions
    merged = (
        debt_pos.merge(vlh_flags, on="folio", how="inner")
        .loc[lambda x: x["folio"].isin(oax_folios)]
        .loc[lambda x: x["unsafe_any"] & x["disagree_any"]]
    )

    n_households = int(merged.shape[0])
    average_amount_pesos = merged["debt_value"].mean()

    return pd.DataFrame(
        {
            "average_amount_pesos": [average_amount_pesos],
            "n_households": [n_households],
        }
    )