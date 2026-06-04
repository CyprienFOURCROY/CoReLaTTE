import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_inr = tables["ii_inr"]

    # Aggregate household-level indicators and amounts
    agg_in = (
        df_in[["folio", "in03a", "in02a10"]]
        .groupby("folio", as_index=False)
        .agg(
            received_liconsa=("in03a", lambda s: (s == 1).any()),
            in02a10=("in02a10", "max"),
        )
    )

    agg_inr = (
        df_inr[["folio", "inr02a"]]
        .groupby("folio", as_index=False)
        .agg(produced_dairy=("inr02a", lambda s: (s == 1).any()))
    )

    # Merge conditions: received Liconsa and produced/sold dairy foods
    cond = agg_in.merge(agg_inr, on="folio", how="inner")
    cond = cond[(cond["received_liconsa"]) & (cond["produced_dairy"])]
    cond = cond[cond["in02a10"].notna() & (cond["in02a10"] > 0)]

    # Top 10 by direct amount from Other Government Program
    top10 = cond.sort_values(["in02a10", "folio"], ascending=[False, True]).head(10).copy()

    # Average age per household
    ages = (
        df_portad.groupby("folio", as_index=False)
        .agg(average_age=("edad", "mean"))
    )

    result = top10.merge(ages, on="folio", how="left")
    result = result[["folio", "in02a10", "average_age"]].rename(
        columns={"in02a10": "direct_amount_other_government_program"}
    )

    return result