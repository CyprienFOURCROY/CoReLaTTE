import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_inr = tables["ii_inr"]

    # Households with reported value for total debts + interests
    debt_hh = df_crh.loc[
        (df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna()),
        ["folio"]
    ].drop_duplicates()

    # Oldest interviewed member per household
    oldest = (
        df_portad[["folio", "edad"]]
        .groupby("folio", as_index=False)["edad"]
        .max()
        .rename(columns={"edad": "oldest_age"})
    )

    hh = debt_hh.merge(oldest, on="folio", how="left")
    hh = hh[hh["oldest_age"].notna()]

    avg_oldest_age = hh["oldest_age"].mean()

    hh["ge_mean"] = hh["oldest_age"] >= avg_oldest_age

    # Dairy production/sales in last 12 months
    dairy = df_inr[["folio", "inr02a"]].copy()
    dairy["dairy"] = dairy["inr02a"].map({1.0: "Yes", 3.0: "No"})

    mm = hh.merge(dairy[["folio", "dairy"]], on="folio", how="left")
    mm = mm[mm["dairy"].notna() & mm["ge_mean"]]

    result = (
        mm.groupby("dairy", as_index=False)
        .agg(households=("folio", "nunique"))
        .rename(columns={"dairy": "produced_sold_dairy_12m", "households": "count"})
    )

    return result