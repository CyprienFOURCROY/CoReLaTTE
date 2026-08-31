import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]

    # Household to state mapping
    df_ent = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])

    # Motor vehicle ownership per household
    df_mv = df_ah[["folio", "ah03d"]].drop_duplicates(subset=["folio"])

    # Plot/land use per household
    df_plot = df_su[["folio", "su01"]].drop_duplicates(subset=["folio"])

    # Merge and filter households that own a motor vehicle
    df = df_ent.merge(df_mv, on="folio", how="inner").merge(df_plot, on="folio", how="left")
    df_mv_only = df[df["ah03d"] == 1.0].copy()

    if df_mv_only.empty:
        return pd.DataFrame({"ent": pd.Series(dtype="Int64"),
                             "households_with_mv_and_plot": pd.Series(dtype="Int64")})

    # Aggregate counts per state
    agg = df_mv_only.groupby("ent").agg(
        mv_count=("folio", "nunique"),
        both_count=("su01", lambda s: int((s == 1.0).sum()))
    )

    # States with at least 20 households owning a motor vehicle
    eligible = agg[agg["mv_count"] >= 20].copy()

    if eligible.empty:
        return pd.DataFrame({"ent": pd.Series(dtype="Int64"),
                             "households_with_mv_and_plot": pd.Series(dtype="Int64")})

    avg_both = eligible["both_count"].mean()

    result = eligible[eligible["both_count"] > avg_both].reset_index()[["ent", "both_count"]]
    result = result.rename(columns={"both_count": "households_with_mv_and_plot"})
    # Cast ent to integer if possible
    result["ent"] = result["ent"].astype("Int64")
    result["households_with_mv_and_plot"] = result["households_with_mv_and_plot"].astype("Int64")

    return result