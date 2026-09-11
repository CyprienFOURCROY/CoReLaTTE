import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]

    eligible_folios = df_su.loc[df_su["su01"] == 1.0, "folio"].dropna().unique()
    subset = df_portad[df_portad["folio"].isin(eligible_folios)].copy()

    overall_mean_age = subset["edad"].mean()

    older = subset[subset["edad"] > overall_mean_age]

    base = subset[["ent"]].dropna().drop_duplicates()

    stats = older.groupby("ent", as_index=False).agg(
        count_older=("edad", "size"),
        avg_age=("edad", "mean")
    )

    result = base.merge(stats, on="ent", how="left")
    result["count_older"] = result["count_older"].fillna(0).astype("int64")
    result = result.sort_values("ent").reset_index(drop=True)

    return result