def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_su = tables["ii_su"]

    # 1. Households with at least one adult (age 18+)
    adults = df_portad[df_portad["edad"] >= 18]
    hh_with_adult = adults["folio"].unique()

    # 2. Households with a recorded total debt + interests (crh04_2 not null)
    crh_debt = df_crh[~df_crh["crh04_2"].isna()]

    # 3. Only households with at least one adult and a recorded total debt
    eligible_hh = set(hh_with_adult) & set(crh_debt["folio"])
    crh_debt = crh_debt[crh_debt["folio"].isin(eligible_hh)]

    # 4. Compute overall average total debt (crh04_2)
    avg_total_debt = crh_debt["crh04_2"].mean()

    # 5. Filter to those whose debt is at or above the overall average
    crh_debt_high = crh_debt[crh_debt["crh04_2"] >= avg_total_debt]

    # 6. Merge with ii_su to get su01 (use a plot/land for sowing/farming/vegetable)
    su01 = df_su[["folio", "su01"]].drop_duplicates("folio")
    merged = crh_debt_high.merge(su01, on="folio", how="left")

    # 7. Map su01 to Yes/No
    def su01_map(x):
        if x == 1:
            return "Yes"
        elif x == 3:
            return "No"
        else:
            return np.nan

    merged["uses_plot"] = merged["su01"].map(su01_map)

    # 8. Group by uses_plot and compute average total debt and count
    result = (
        merged.groupby("uses_plot", dropna=False)
        .agg(
            average_total_debt=("crh04_2", "mean"),
            household_count=("folio", "nunique")
        )
        .reset_index()
        .rename(columns={"uses_plot": "uses_plot_for_sowing"})
    )

    return result