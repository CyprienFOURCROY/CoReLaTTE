import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_se = tables["ii_se"][["folio", "se01b"]].copy()
    df_ah = tables["ii_ah"][["folio", "ah04d_2"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_2"]].copy()

    # Households in Oaxaca
    oax_folios = (
        df_portad.loc[df_portad["ent"] == 20, ["folio"]]
        .drop_duplicates()
    )

    # Households with disease/accident/hospitalization event in last 5 years
    event_folios = df_se.loc[df_se["se01b"] == 1, ["folio"]]

    # Households with recorded motor vehicle value; aggregate total per household
    mv_values = (
        df_ah.loc[df_ah["ah04d_2"].notna()]
        .groupby("folio", as_index=False)["ah04d_2"]
        .sum()
        .rename(columns={"ah04d_2": "total_mv"})
    )

    # Merge to get target households: Oaxaca + event + recorded MV value
    target = (
        oax_folios.merge(event_folios, on="folio", how="inner")
        .merge(mv_values, on="folio", how="inner")
    )

    # Compute average total motor vehicle value among these households
    mv_avg = target["total_mv"].mean()

    # Keep only households with total MV below this average
    below_avg_mv = target.loc[target["total_mv"] < mv_avg, ["folio"]]

    # Merge debts and compute average total debts plus interests
    debts = below_avg_mv.merge(df_crh, on="folio", how="left")
    avg_debts = debts["crh04_2"].mean(skipna=True)

    return pd.DataFrame({"average_total_debts_plus_interest_pesos": [avg_debts]})