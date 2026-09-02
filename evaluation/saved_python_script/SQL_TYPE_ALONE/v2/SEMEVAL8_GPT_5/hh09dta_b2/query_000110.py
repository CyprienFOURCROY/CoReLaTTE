import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_se = tables["ii_se"]
    df_in = tables["ii_in"]

    # Adults count per household (age >= 18)
    df_adults = df_portad[["folio", "edad"]].copy()
    df_adults["is_adult"] = df_adults["edad"] >= 18
    adults_count = (
        df_adults.groupby("folio", as_index=False)["is_adult"]
        .sum()
        .rename(columns={"is_adult": "n_adults"})
    )
    adults_count["n_adults"] = adults_count["n_adults"].astype("int64")

    # Household-level unique rows
    su_uni = df_su[["folio", "su01", "su231"]].drop_duplicates(subset=["folio"], keep="first")
    se_uni = df_se[["folio", "se01e"]].drop_duplicates(subset=["folio"], keep="first")
    in_uni = df_in[["folio", "in01a10_1"]].drop_duplicates(subset=["folio"], keep="first")

    # Merge and filter households
    hh = su_uni.merge(se_uni, on="folio", how="inner").merge(in_uni, on="folio", how="inner")

    hh_filtered = hh[
        (hh["su01"] == 1.0) &
        (hh["se01e"] == 1.0) &
        (hh["in01a10_1"] == 3.0)
    ].copy()

    # Attach adult counts
    hh_filtered = hh_filtered.merge(adults_count, on="folio", how="inner")

    # Group by number of adults
    result = (
        hh_filtered.groupby("n_adults")
        .agg(
            avg_expense_chemical_fertilizer=("su231", "mean"),
            n_households=("folio", "nunique"),
        )
        .reset_index()
        .sort_values("n_adults")
    )

    return result