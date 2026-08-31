import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_ah = tables["ii_ah"][["folio", "ah04h_2"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_2"]].copy()
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()

    # Households with at least one member aged 60+
    older_df = (
        df_portad.assign(older=(df_portad["edad"] >= 60))
        .groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), older=("older", "max"))
    )

    # Households with at least one member having positive financial assets/afores value
    fin_df = (
        df_ah.assign(finpos=df_ah["ah04h_2"].fillna(0) > 0)
        .groupby("folio", as_index=False)
        .agg(finpos=("finpos", "max"))
    )

    # Debts plus interests per household and overall average
    debt_per_hh = df_crh.groupby("folio", as_index=False)["crh04_2"].max()
    overall_avg_debt = debt_per_hh["crh04_2"].mean(skipna=True)
    debt_df = debt_per_hh.assign(debts_above_avg=debt_per_hh["crh04_2"] > overall_avg_debt)[
        ["folio", "debts_above_avg"]
    ]

    # Received any direct income from Other Government Program
    income_df = (
        df_in.assign(received_other=df_in["in02a10"].fillna(0) > 0)
        .groupby("folio", as_index=False)
        .agg(received_other=("received_other", "max"))
    )

    # Merge all and determine eligibility
    merged = (
        older_df.merge(fin_df, on="folio", how="left")
        .merge(debt_df, on="folio", how="left")
        .merge(income_df, on="folio", how="left")
    )

    for col in ["finpos", "debts_above_avg", "received_other"]:
        merged[col] = merged[col].fillna(False)

    merged = merged[merged["ent"].notna()]
    merged["eligible"] = merged["older"] & merged["finpos"] & merged["debts_above_avg"]

    eligible = merged[merged["eligible"]]

    result = (
        eligible.groupby("ent", as_index=False)
        .agg(
            households_count=("folio", "nunique"),
            households_received_other_direct=("received_other", "sum"),
        )
        .sort_values("ent")
        .reset_index(drop=True)
    )

    return result