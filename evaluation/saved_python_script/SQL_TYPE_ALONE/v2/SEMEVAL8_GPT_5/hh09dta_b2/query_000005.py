import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()
    df_crh = df_crh[(df_crh["crh04_1"] == 1) & (df_crh["crh04_2"].notna())]

    if df_crh.empty:
        return pd.DataFrame(columns=["state", "avg_total_debt_pesos", "n_households"])

    overall_avg = df_crh["crh04_2"].mean()

    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_portad = df_portad.dropna(subset=["ent"]).drop_duplicates(subset=["folio"])

    df = df_crh.merge(df_portad, on="folio", how="left").dropna(subset=["ent"])
    if df.empty:
        return pd.DataFrame(columns=["state", "avg_total_debt_pesos", "n_households"])

    df["ent"] = df["ent"].astype("Int64")

    by_state = (
        df.groupby("ent", dropna=False)
        .agg(avg_total_debt_pesos=("crh04_2", "mean"), n_households=("folio", "nunique"))
        .reset_index()
    )

    result = by_state[by_state["avg_total_debt_pesos"] > overall_avg].copy()
    result = result.rename(columns={"ent": "state"})
    result = result.sort_values("avg_total_debt_pesos", ascending=False).reset_index(drop=True)
    return result[["state", "avg_total_debt_pesos", "n_households"]]