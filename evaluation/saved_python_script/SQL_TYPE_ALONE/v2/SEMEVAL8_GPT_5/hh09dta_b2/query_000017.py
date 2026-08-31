import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Households with at least one adult (18+)
    adult_folios = pd.Index(df_portad.loc[df_portad["edad"] >= 18, "folio"].dropna().unique())

    # Households with recorded total debt + interest
    df_debt = df_crh[["folio", "crh04_2"]].dropna(subset=["crh04_2"])
    df_debt = df_debt.groupby("folio", as_index=False)["crh04_2"].first()

    # Keep only households with adults
    df_debt = df_debt[df_debt["folio"].isin(adult_folios)]

    # Overall average among adult households with recorded debt
    overall_avg = df_debt["crh04_2"].mean()

    # Filter to households with debt >= overall average
    df_high = df_debt[df_debt["crh04_2"] >= overall_avg].copy()

    # Merge with plot/land use indicator
    df_su_sub = df_su[["folio", "su01"]].groupby("folio", as_index=False).first()
    merged = df_high.merge(df_su_sub, on="folio", how="left")
    merged = merged[merged["su01"].isin([1.0, 3.0])]
    merged["uses_plot"] = merged["su01"].map({1.0: "Yes", 3.0: "No"})

    # Aggregate: average total debt and household count by plot/land use
    result = (
        merged.groupby("uses_plot")
        .agg(average_total_debt=("crh04_2", "mean"), household_count=("folio", "nunique"))
        .reset_index()
    )

    return result