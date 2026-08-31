import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"][["folio", "su01", "su234"]].copy()
    df_ah = tables["ii_ah"][["folio", "ah03d"]].copy()

    # Aggregate motor vehicle ownership at household level (Yes if any record says 1)
    df_ah_agg = (
        df_ah.dropna(subset=["folio"])
        .groupby("folio", as_index=False)["ah03d"]
        .min()
    )

    # Compute overall average seed expense among farming households with positive seed expenses
    df_avg_source = df_su[(df_su["su01"] == 1.0) & (df_su["su234"] > 0)]
    avg_seed_expense = df_avg_source["su234"].mean()

    # If no valid average (no farming households with positive expenses), return empty result
    if pd.isna(avg_seed_expense):
        return pd.DataFrame({"folio": pd.Series(dtype="object"), "su234": pd.Series(dtype="float64")})

    # Merge and filter households: farming, own motor vehicle, positive seed expenses below average
    merged = df_su.merge(df_ah_agg, on="folio", how="inner")
    result = merged[
        (merged["su01"] == 1.0)
        & (merged["ah03d"] == 1.0)
        & (merged["su234"] > 0)
        & (merged["su234"] < avg_seed_expense)
    ][["folio", "su234"]].copy()

    # Optional: sort by expense for readability
    result = result.sort_values(by="su234", ascending=True, kind="mergesort").reset_index(drop=True)

    return result