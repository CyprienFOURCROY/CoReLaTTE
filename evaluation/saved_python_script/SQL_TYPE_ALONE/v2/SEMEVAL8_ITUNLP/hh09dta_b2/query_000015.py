import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_inr = tables["ii_inr"].copy()
    df_nna = tables["ii_nna"].copy()

    # Households with dairy production/sales in last 12 months
    df_hh_dairy = (
        df_inr.loc[df_inr["inr02a"] == 1.0, ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"])
    )

    # Aggregate to household-level info from ii_portad
    df_portad_hh = (
        df_portad.dropna(subset=["folio"])
        .groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), edad=("edad", "mean"))
    )

    # Merge to attach state and age
    df_merge = df_hh_dairy.merge(df_portad_hh, on="folio", how="left")

    # Attach non-ag business ownership info
    df_nna_hh = (
        df_nna[["folio", "nna01"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"])
    )
    df_merge = df_merge.merge(df_nna_hh, on="folio", how="left")

    # Indicator for non-ag business ownership
    df_merge["has_nonag"] = (df_merge["nna01"] == 1.0).astype(int)

    # Group by state
    res = (
        df_merge.groupby("ent", dropna=False)
        .agg(
            n_households=("folio", "nunique"),
            avg_household_age=("edad", "mean"),
            households_with_nonag=("has_nonag", "sum"),
        )
        .reset_index()
    )

    # Order and take top 10 states
    res = res.sort_values(["n_households", "ent"], ascending=[False, True]).head(10)

    return res