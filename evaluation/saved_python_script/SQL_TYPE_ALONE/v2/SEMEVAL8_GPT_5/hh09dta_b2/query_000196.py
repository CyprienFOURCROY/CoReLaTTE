import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].drop_duplicates(subset=["folio"]).copy()
    df_se = tables["ii_se"][["folio", "se01d"]].copy()
    df_su = tables["ii_su"][["folio", "su01", "su234"]].copy()

    se_filtered = df_se[df_se["se01d"] == 1.0]
    su_filtered = df_su[df_su["su01"] == 1.0]

    df = su_filtered.merge(se_filtered, on="folio", how="inner").merge(df_portad, on="folio", how="left")
    df = df[~df["ent"].isna()].copy()

    df["seeds"] = df["su234"].fillna(0)

    overall_avg = df["seeds"].mean()

    grouped = (
        df.groupby("ent")
        .agg(
            household_count=("folio", "nunique"),
            avg_seeds_expense=("seeds", "mean"),
        )
        .reset_index()
    )

    result = grouped[(grouped["household_count"] >= 10) & (grouped["avg_seeds_expense"] > overall_avg)].copy()
    result = result.sort_values("avg_seeds_expense", ascending=False).reset_index(drop=True)
    result["ent"] = result["ent"].astype("Int64")

    return result