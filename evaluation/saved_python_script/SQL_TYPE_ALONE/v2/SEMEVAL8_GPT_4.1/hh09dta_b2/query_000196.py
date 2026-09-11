def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_su = tables["ii_su"]

    # 1. Households that use agricultural plots: su01 == 1
    df_su_agri = df_su[df_su["su01"] == 1]

    # 2. Households that reported losing home/business to natural disaster in last 5 years: se01d == 1
    df_se_disaster = df_se[df_se["se01d"] == 1]

    # 3. Merge on folio to get intersection
    df_merge = df_su_agri.merge(df_se_disaster[["folio"]], on="folio", how="inner")

    # 4. Merge with portad to get state info
    df_merge = df_merge.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # 5. Group by state, calculate household count and average seeds expense (su234)
    # Only consider non-null su234 for average, but count all households
    grouped = df_merge.groupby("ent").agg(
        household_count=("folio", "nunique"),
        avg_seeds_expense=("su234", "mean")
    ).reset_index()

    # 6. Compute overall average seeds expense across all selected households (not by state)
    overall_avg = df_merge["su234"].mean()

    # 7. Filter states with at least 10 households and avg_seeds_expense > overall_avg
    result = grouped[
        (grouped["household_count"] >= 10) &
        (grouped["avg_seeds_expense"] > overall_avg)
    ].copy()

    # 8. Sort by avg_seeds_expense descending
    result = result.sort_values(by="avg_seeds_expense", ascending=False)

    # 9. Rename columns for clarity
    result = result.rename(columns={
        "ent": "state",
        "household_count": "household_count",
        "avg_seeds_expense": "avg_seeds_expense"
    })

    # 10. Reset index for clean output
    result = result.reset_index(drop=True)

    return result[["state", "household_count", "avg_seeds_expense"]]